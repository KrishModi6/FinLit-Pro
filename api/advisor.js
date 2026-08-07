import OpenAI from 'openai'

/**
 * POST /api/advisor
 * Body: { messages: [{ role: 'user' | 'assistant', content: string }, ...] }
 *
 * Streams a plain-text response.
 *
 * The API key lives only in the OPENAI_API_KEY environment variable on the
 * server. It is never sent to the browser, which is the entire reason this
 * endpoint exists rather than calling the model provider from the page.
 */

// Streaming keeps us clear of the platform's function timeout on long answers.
export const maxDuration = 60

// Override with OPENAI_MODEL if you want a different tier. If the primary is
// not available to the key, we retry once on a broadly available fallback
// rather than failing the request.
const MODEL = process.env.OPENAI_MODEL || 'gpt-5'
const FALLBACK_MODEL = 'gpt-4o'

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
- Never use em dashes. The whole site avoids them.

## The course you can point to
Beginner: what a stock is, how the market works, why prices move, brokerages and quotes, indices and market cycles, dividends and time horizon, know your risk profile, buying your first share, recap.
Intermediate: stable vs unstable stocks, beta, fundamental analysis, technical analysis, ETFs and diversification, why you keep a stable core, the GameStop vs boring case study, recap.
Examples: Roblox's round trip, GameStop after the crowd left, the boring chart that beat both, recap. These use real live charts.
Hard: what high-risk investing is, options basics, risk/reward and position sizing, when a risky bet makes sense, when bets go bad (GameStop and Enron), investor psychology, building a risky sleeve, a full options trade walkthrough, recap.

Refer to lessons by name when relevant.`

function bad(res, status, message) {
  res.status(status).json({ error: message })
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST')
    return bad(res, 405, 'Method not allowed')
  }

  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    return bad(
      res,
      503,
      'The AI Advisor is not configured yet. An OPENAI_API_KEY environment variable needs to be set on the deployment.'
    )
  }

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
  const history = incoming
    .slice(-MAX_TURNS)
    .filter((m) => (m?.role === 'user' || m?.role === 'assistant') && typeof m.content === 'string')
    .map((m) => ({ role: m.role, content: m.content.slice(0, MAX_CHARS) }))

  if (!history.length || history[0].role !== 'user') {
    return bad(res, 400, 'The conversation must start with a user message.')
  }

  const client = new OpenAI({ apiKey })
  const messages = [{ role: 'system', content: SYSTEM }, ...history]

  let wroteAny = false

  const run = async (model) => {
    const stream = await client.chat.completions.create({
      model,
      messages,
      max_completion_tokens: 1200,
      stream: true,
    })

    let finish = null
    for await (const chunk of stream) {
      const choice = chunk.choices?.[0]
      const text = choice?.delta?.content
      if (choice?.finish_reason) finish = choice.finish_reason
      if (!text) continue
      if (!wroteAny) {
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.setHeader('Cache-Control', 'no-store')
        res.setHeader('X-Accel-Buffering', 'no')
        wroteAny = true
      }
      res.write(text)
    }
    return finish
  }

  try {
    let finish
    try {
      finish = await run(MODEL)
    } catch (err) {
      // A key without access to the primary model should still get an answer
      // rather than an error page.
      const unknownModel =
        !wroteAny &&
        (err?.status === 404 ||
          (err?.status === 400 && /model/i.test(err?.message ?? '')))
      if (!unknownModel) throw err
      finish = await run(FALLBACK_MODEL)
    }

    const append = (text) => {
      if (!wroteAny) {
        res.setHeader('Content-Type', 'text/plain; charset=utf-8')
        res.setHeader('Cache-Control', 'no-store')
        wroteAny = true
      }
      res.write(text)
    }

    if (finish === 'length') {
      append('\n\n(Cut off there. Ask me to continue if you want the rest.)')
    } else if (finish === 'content_filter') {
      append(
        (wroteAny ? '\n\n' : '') +
          'I am not able to answer that one. If it was about a specific investment decision, that is deliberate: I can explain how to think about it, but not what to do.'
      )
    } else if (!wroteAny) {
      append('I did not get a response that time. Please try asking again.')
    }

    return res.end()
  } catch (err) {
    if (!wroteAny && !res.headersSent) {
      const status =
        err?.status === 401 ? 503 : err?.status === 429 ? 429 : err?.status === 400 ? 400 : 502
      return bad(
        res,
        status,
        status === 503
          ? 'The configured API key was rejected. Check OPENAI_API_KEY on the deployment.'
          : status === 429
            ? 'Rate limited, or the account is out of credit. Wait a moment and try again.'
            : status === 400
              ? `The model rejected the request: ${err?.message ?? 'unknown reason'}`
              : 'The advisor is temporarily unavailable.'
      )
    }
    res.write('\n\n(The connection dropped before I finished. Please try again.)')
    return res.end()
  }
}
