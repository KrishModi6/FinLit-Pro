import Anthropic from '@anthropic-ai/sdk'

/**
 * POST /api/advisor
 * Body: { messages: [{ role: 'user' | 'assistant', content: string }, ...] }
 *
 * Streams a plain-text response.
 *
 * The API key lives only in the ANTHROPIC_API_KEY environment variable on the
 * server. It is never sent to the browser, which is the entire reason this
 * endpoint exists rather than calling Anthropic from the page.
 */

// Streaming keeps us clear of the platform's function timeout on long answers.
export const maxDuration = 60

const MODEL = 'claude-opus-5'
const MAX_TURNS = 20
const MAX_CHARS = 4000

const SYSTEM = `You are the AI Advisor for Stock Guide, a free stock market course written by Krish Modi, a high school student, for other students. You are talking to a teenager or young adult who is learning, not to a client.

## What you are for
Explain how markets and investing work, in the same voice as the course: warm and direct like a smart older classmate, but precise where precision matters. Use concrete numbers and worked examples rather than vague reassurance.

## The hard line you never cross
You are not a financial adviser and you never give personalised investment advice. That means:
- Never tell someone whether to buy, sell, or hold any specific security, and never say what you "would" do.
- Never recommend an allocation for their actual money, predict a price, or tell them whether now is a good time.
- If asked any of those, say plainly that you cannot advise on individual decisions, then teach the framework they would need to reason about it themselves, and point them at the relevant lesson.
This is not a formality. The audience is young and may take what you say literally.

## How to answer
- Lead with the direct answer, then the reasoning. Do not open with a preamble.
- Keep it to a few short paragraphs unless genuinely asked for depth. This renders in a small chat panel.
- Work through arithmetic explicitly when numbers are involved.
- Name the trade-off. Every strategy costs something, and the course's whole argument is that the cost is what people fail to think about.
- Never hype. Never imply an easy path to money. When something is mostly luck, say so.
- If you do not know, or the answer depends on facts you cannot see (current prices, their circumstances, their country's tax rules), say that instead of guessing.
- Use plain text. No markdown headers or tables; short paragraphs and the occasional dash list only.

## The course you can point to
Beginner: what a stock is, how the market works, why prices move, brokerages and quotes, indices and market cycles, dividends and time horizon, know your risk profile, buying your first share.
Intermediate: stable vs unstable stocks, beta, fundamental analysis, technical analysis, ETFs and diversification, why you keep a stable core, the GameStop vs boring case study.
Hard: what high-risk investing is, options basics, risk/reward and position sizing, when a risky bet makes sense, when bets go bad (GameStop and Enron), investor psychology, building a risky sleeve, and a full options trade walkthrough.

Refer to lessons by name when relevant.`

function bad(res, status, message) {
  res.status(status).json({ error: message })
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST')
    return bad(res, 405, 'Method not allowed')
  }

  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) {
    return bad(
      res,
      503,
      'The AI Advisor is not configured yet. An ANTHROPIC_API_KEY environment variable needs to be set on the deployment.'
    )
  }

  // Vercel parses JSON bodies; guard anyway in case of a raw body.
  let body = req.body
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body)
    } catch {
      return bad(res, 400, 'Body must be JSON.')
    }
  }

  const incoming = Array.isArray(body?.messages) ? body.messages : null
  if (!incoming || incoming.length === 0) {
    return bad(res, 400, 'Send a non-empty messages array.')
  }

  // Bound the conversation so one tab cannot run up an unbounded bill.
  const messages = incoming
    .slice(-MAX_TURNS)
    .filter((m) => (m?.role === 'user' || m?.role === 'assistant') && typeof m.content === 'string')
    .map((m) => ({ role: m.role, content: m.content.slice(0, MAX_CHARS) }))

  if (!messages.length || messages[0].role !== 'user') {
    return bad(res, 400, 'The conversation must start with a user message.')
  }

  const client = new Anthropic({ apiKey })

  const base = {
    model: MODEL,
    max_tokens: 4000,
    system: SYSTEM,
    messages,
    // Claude Opus 5 thinks by default; medium effort keeps a chat answer
    // quick without the failure modes that come from disabling thinking.
    output_config: { effort: 'medium' },
  }

  /**
   * With `withFallbacks`, a request declined by a safety classifier is re-run
   * server-side on the recommended model instead of returning a refusal. That
   * rides a beta header, so if the account does not have the beta enabled we
   * fall back to a plain request rather than losing the advisor entirely.
   */
  const open = (withFallbacks) =>
    withFallbacks
      ? client.beta.messages.stream({
          ...base,
          betas: ['server-side-fallback-2026-07-01'],
          fallbacks: 'default',
        })
      : client.messages.stream(base)

  let wroteAny = false

  const run = async (withFallbacks) => {
    const stream = open(withFallbacks)

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta?.type === 'text_delta') {
        if (!wroteAny) {
          res.setHeader('Content-Type', 'text/plain; charset=utf-8')
          res.setHeader('Cache-Control', 'no-store')
          res.setHeader('X-Accel-Buffering', 'no')
          wroteAny = true
        }
        res.write(event.delta.text)
      }
    }
    return stream.finalMessage()
  }

  try {
    let final
    try {
      final = await run(true)
    } catch (err) {
      // Only worth retrying if the beta itself was rejected and we have not
      // started streaming to the reader yet.
      const betaRejected =
        !wroteAny && err?.status === 400 && /fallback|beta/i.test(err?.message ?? '')
      if (!betaRejected) throw err
      final = await run(false)
    }

    // Append a note without assuming headers were already sent: a refusal can
    // arrive with no text at all, in which case nothing has been written yet.
    const append = (text) => {
      if (!wroteAny) {
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.setHeader('Cache-Control', 'no-store')
        wroteAny = true
      }
      res.write(text)
    }

    // A refusal arrives as a successful response with empty or partial content,
    // so it has to be checked explicitly rather than caught.
    if (final.stop_reason === 'refusal') {
      append(
        (wroteAny ? '\n\n' : '') +
          'I am not able to answer that one. If it was about a specific investment decision, ' +
          'that is deliberate: I can explain how to think about it, but not what to do.'
      )
    } else if (final.stop_reason === 'max_tokens') {
      append('\n\n(Cut off there. Ask me to continue if you want the rest.)')
    } else if (!wroteAny) {
      append('I did not get a response that time. Please try asking again.')
    }

    return res.end()
  } catch (err) {
    // If nothing has reached the reader we can still send a real status code.
    if (!wroteAny && !res.headersSent) {
      const status = err?.status === 401 ? 503 : err?.status === 429 ? 429 : 502
      return bad(
        res,
        status,
        status === 503
          ? 'The configured API key was rejected. Check ANTHROPIC_API_KEY on the deployment.'
          : status === 429
            ? 'Rate limited. Wait a moment and try again.'
            : 'The advisor is temporarily unavailable.'
      )
    }
    res.write('\n\n(The connection dropped before I finished. Please try again.)')
    return res.end()
  }
}
