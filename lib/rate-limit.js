/**
 * Rate limiting for the AI Advisor.
 *
 * The advisor is a public POST endpoint that spends real OpenAI credit. Each
 * request is already bounded (20 turns, 4000 chars each, 1200 output tokens),
 * but nothing stopped one script from making a hundred thousand of them.
 *
 * Two limits, because they defend against different things:
 *
 *   Per visitor  stops one person hammering it, and is the one a real reader
 *                could ever notice. Generous on purpose.
 *   Global daily is the actual wallet protection. Per-IP limits are worth
 *                little against a distributed script or a spoofed header, so
 *                there is a hard ceiling on spend per day regardless of who
 *                is asking.
 *
 * Storage is Upstash Redis over its REST API when the environment provides
 * credentials, and an in-process Map otherwise. The fallback matters: a
 * serverless deployment runs many instances, so an in-memory counter only
 * sees a fraction of traffic and a determined abuser gets through. It is a
 * speed bump, not a lock. Provision Upstash (Vercel's marketplace wires the
 * variables up automatically, and the free tier is 500K commands a month)
 * to make the limits actually hold.
 *
 * No SDK: Upstash speaks plain HTTP, so this is a fetch call and one less
 * dependency to keep current.
 */

const REDIS_URL = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL
const REDIS_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN

const num = (value, fallback) => {
  const n = Number(value)
  return Number.isFinite(n) && n > 0 ? n : fallback
}

export const PER_IP_LIMIT = num(process.env.ADVISOR_PER_IP_LIMIT, 12)
export const PER_IP_WINDOW_S = num(process.env.ADVISOR_PER_IP_WINDOW_S, 600) // 10 minutes
export const GLOBAL_DAILY_LIMIT = num(process.env.ADVISOR_GLOBAL_DAILY_LIMIT, 1000)

export const usingRedis = Boolean(REDIS_URL && REDIS_TOKEN)

/**
 * Best guess at who is asking.
 *
 * `x-real-ip` is set by Vercel's proxy and cannot be overridden by the caller,
 * so it is preferred. `x-forwarded-for` is a fallback for other hosts and its
 * leftmost entry IS caller-controlled, which is part of why the global cap
 * exists rather than trusting this alone.
 */
export function clientKey(req) {
  // Defensive because this runs before the try block in checkRateLimit, so
  // anything thrown here would escape the fail-open guarantee and 500 a
  // request that should simply have been allowed through.
  const headers = req?.headers ?? {}

  const real = headers['x-real-ip']
  if (typeof real === 'string' && real.trim()) return real.trim()

  const fwd = headers['x-forwarded-for']
  const first = (Array.isArray(fwd) ? fwd[0] : fwd || '').split(',')[0].trim()
  return first || 'unknown'
}

// ---- In-process fallback ----------------------------------------------------

const memory = new Map() // key -> { count, expiresAt }

function memoryIncrement(key, ttlSeconds, now) {
  const existing = memory.get(key)
  if (!existing || existing.expiresAt <= now) {
    memory.set(key, { count: 1, expiresAt: now + ttlSeconds * 1000 })
    return 1
  }
  existing.count += 1
  return existing.count
}

/** Drop expired entries so a long-lived instance cannot grow without bound. */
function sweepMemory(now) {
  if (memory.size < 5000) return
  for (const [key, entry] of memory) if (entry.expiresAt <= now) memory.delete(key)
}

// ---- Upstash ----------------------------------------------------------------

/**
 * INCR each key and give it a TTL, in one round trip.
 * Returns the resulting counts in the order the keys were passed.
 */
async function redisIncrement(entries) {
  const commands = entries.flatMap(({ key, ttl }) => [
    ['INCR', key],
    ['EXPIRE', key, String(ttl)],
  ])

  const res = await fetch(`${REDIS_URL}/pipeline`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${REDIS_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(commands),
    signal: AbortSignal.timeout(2000),
  })

  if (!res.ok) throw new Error(`Upstash responded ${res.status}`)
  const payload = await res.json()
  // Pipeline returns one entry per command; the INCRs are at even indices.
  return entries.map((_, i) => Number(payload[i * 2]?.result))
}

// ---- Public API -------------------------------------------------------------

/**
 * Counts this request against both limits.
 *
 * Returns `{ allowed }`, plus `retryAfter` in seconds and a `reason` when it
 * is refused. Fails OPEN: if the limiter itself errors, the request is let
 * through rather than taking the advisor down over a bookkeeping problem.
 * The per-request token cap means a limiter outage cannot become a runaway
 * bill on its own.
 */
export async function checkRateLimit(req, now = Date.now()) {
  const ip = clientKey(req)
  const windowIndex = Math.floor(now / (PER_IP_WINDOW_S * 1000))
  const day = new Date(now).toISOString().slice(0, 10)

  const ipKey = `advisor:ip:${ip}:${windowIndex}`
  const globalKey = `advisor:global:${day}`

  // Seconds left in the current window, so the TTL never outlives it.
  const ipTtl = Math.max(1, PER_IP_WINDOW_S - Math.floor((now % (PER_IP_WINDOW_S * 1000)) / 1000))
  const globalTtl = 86_400

  try {
    sweepMemory(now)
    const bump = async (key, ttl) =>
      usingRedis ? (await redisIncrement([{ key, ttl }]))[0] : memoryIncrement(key, ttl, now)

    // Per visitor first, and the global counter is only touched once that
    // passes. Order matters: counting refused requests against the shared
    // daily budget would let one script exhaust it with requests that never
    // reach the model, taking the advisor down for everybody else at no cost
    // to the attacker. Only requests that are actually about to spend money
    // are allowed to consume the money budget.
    const ipCount = await bump(ipKey, ipTtl)
    if (Number.isFinite(ipCount) && ipCount > PER_IP_LIMIT) {
      return {
        allowed: false,
        reason: 'ip',
        retryAfter: ipTtl,
        message: `That is ${PER_IP_LIMIT} questions in ${Math.round(
          PER_IP_WINDOW_S / 60
        )} minutes, which is the limit. Try again in ${Math.ceil(ipTtl / 60)} minutes.`,
      }
    }

    const globalCount = await bump(globalKey, globalTtl)
    if (Number.isFinite(globalCount) && globalCount > GLOBAL_DAILY_LIMIT) {
      return {
        allowed: false,
        reason: 'global',
        retryAfter: 3600,
        message:
          'The advisor has hit its daily limit for everyone. It is a free tool with a capped budget, so it will be back tomorrow. Every other part of the course still works.',
      }
    }

    return { allowed: true, ipCount, globalCount }
  } catch {
    // Bookkeeping failed. Let the question through.
    return { allowed: true, degraded: true }
  }
}
