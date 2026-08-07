/**
 * Tests for the advisor's rate limiter.  Run with `npm test`.
 *
 * No test framework: this is one pure module with no DOM and no React, so a
 * plain Node script that exits non-zero is enough, and it adds no
 * dependencies to keep current.
 *
 * Both storage backends are covered. The Upstash path matters most, because
 * it is the one that runs in production once credentials exist and would
 * otherwise never be exercised until it mattered. Its transport is stubbed,
 * so this needs no network and no database.
 */

let pass = 0
let fail = 0
const check = (label, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want)
  ok ? pass++ : fail++
  console.log(`  ${ok ? 'ok  ' : 'FAIL'}  ${label}${ok ? '' : `   got=${JSON.stringify(got)} want=${JSON.stringify(want)}`}`)
}
const section = (t) => console.log(`\n${t}`)

const LIB = new URL('../lib/rate-limit.js', import.meta.url).href
const req = (ip) => ({ headers: { 'x-real-ip': ip } })
const T0 = Date.UTC(2026, 7, 7, 12, 0, 0)
const DAY = 86_400_000

// ---------------------------------------------------------------------------
// In-memory fallback
// ---------------------------------------------------------------------------
process.env.ADVISOR_PER_IP_LIMIT = '3'
process.env.ADVISOR_PER_IP_WINDOW_S = '60'
process.env.ADVISOR_GLOBAL_DAILY_LIMIT = '6'

const mem = await import(`${LIB}?memory`)
check('falls back to memory with no credentials', mem.usingRedis, false)

section('per-visitor limit (3 per 60s)')
for (let i = 1; i <= 5; i++) {
  check(`request ${i}`, (await mem.checkRateLimit(req('1.1.1.1'), T0)).allowed, i <= 3)
}

section('refused requests must not consume the shared daily budget')
// Five attempts above, three allowed, so exactly three of the budget is spent.
// Counting the refusals would let a script exhaust the budget for free and
// take the advisor down for everyone.
const probe = await mem.checkRateLimit(req('2.2.2.2'), T0)
check('a different visitor still gets through', probe.allowed, true)
check('global spend is 4, not 6', probe.globalCount, 4)

section('windows roll over')
check('same visitor, next window', (await mem.checkRateLimit(req('1.1.1.1'), T0 + 60_000)).allowed, true)

section('global daily cap (6)')
check('at the cap', (await mem.checkRateLimit(req('3.3.3.3'), T0 + 60_000)).allowed, true)
const over = await mem.checkRateLimit(req('4.4.4.4'), T0 + 60_000)
check('over the cap is refused', over.allowed, false)
check('refusal names the global cap', over.reason, 'global')
check('refusal carries a positive Retry-After', over.retryAfter > 0, true)
check('a new day clears it', (await mem.checkRateLimit(req('4.4.4.4'), T0 + DAY)).allowed, true)

section('identifying the caller')
check('prefers x-real-ip, which the proxy sets',
  mem.clientKey({ headers: { 'x-real-ip': '5.5.5.5', 'x-forwarded-for': '6.6.6.6' } }), '5.5.5.5')
check('falls back to leftmost x-forwarded-for',
  mem.clientKey({ headers: { 'x-forwarded-for': '7.7.7.7, 8.8.8.8' } }), '7.7.7.7')
check('tolerates no headers', mem.clientKey({ headers: {} }), 'unknown')

section('fails open rather than 500ing')
check('a request with no headers object at all',
  (await mem.checkRateLimit({}, T0 + 3 * DAY)).allowed, true)

// ---------------------------------------------------------------------------
// Upstash path, transport stubbed
// ---------------------------------------------------------------------------
process.env.UPSTASH_REDIS_REST_URL = 'https://stub.upstash.io'
process.env.UPSTASH_REDIS_REST_TOKEN = 'stub-token'

const sent = []
let counter = 0
let failNext = false
const realFetch = globalThis.fetch
globalThis.fetch = async (url, options) => {
  if (failNext) throw new Error('network down')
  const commands = JSON.parse(options.body)
  sent.push({ url, commands, auth: options.headers.Authorization })
  // One result per command; INCR replies with the new count.
  return {
    ok: true,
    json: async () => commands.map((c) => ({ result: c[0] === 'INCR' ? ++counter : 1 })),
  }
}

const redis = await import(`${LIB}?redis`)
section('Upstash backend')
check('detects credentials', redis.usingRedis, true)

await redis.checkRateLimit(req('1.2.3.4'), T0)
check('posts to the pipeline endpoint', sent[0].url, 'https://stub.upstash.io/pipeline')
check('sends a bearer token', sent[0].auth, 'Bearer stub-token')
check('increments then expires', sent[0].commands.map((c) => c[0]), ['INCR', 'EXPIRE'])
check('keys the window by visitor', sent[0].commands[0][1].startsWith('advisor:ip:1.2.3.4:'), true)
check('TTL never outlives the window', Number(sent[0].commands[1][2]) <= 60, true)
check('bumps the global key only after the visitor passes',
  sent[1].commands[0][1], 'advisor:global:2026-08-07')

section('Upstash outage')
failNext = true
check('lets the question through rather than failing the request',
  (await redis.checkRateLimit(req('9.9.9.9'), T0)).allowed, true)
check('flags itself as degraded', (await redis.checkRateLimit(req('9.9.9.9'), T0)).degraded, true)
failNext = false
globalThis.fetch = realFetch

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
