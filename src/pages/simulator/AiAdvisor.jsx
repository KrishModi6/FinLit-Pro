import { useEffect, useRef, useState } from 'react'
import { Panel } from '../../components/ui/SimUI.jsx'
import { ArrowRightIcon } from '../../components/ui/Icons.jsx'
import { getTool } from '../../data/simulator.js'

/**
 * Chat against /api/advisor, which streams plain text.
 *
 * The API key lives server-side only; this component never sees it. If the
 * deployment has no key configured the endpoint returns a clear 503 and we
 * surface that message rather than failing silently.
 */
const STARTERS = [
  'What actually happens when I press buy?',
  'Why did the stock fall when earnings beat expectations?',
  'Explain theta decay like I have never traded an option.',
  'How do I work out if a position is too big?',
]

export default function AiAdvisor() {
  const tool = getTool('advisor')
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState(null)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, streaming])

  async function send(text) {
    const question = text.trim()
    if (!question || streaming) return

    setError(null)
    setDraft('')
    const next = [...messages, { role: 'user', content: question }]
    setMessages([...next, { role: 'assistant', content: '' }])
    setStreaming(true)

    try {
      const res = await fetch('/api/advisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next }),
      })

      if (!res.ok) {
        let msg = 'The advisor is unavailable right now.'
        try {
          const body = await res.json()
          if (body?.error) msg = body.error
        } catch {
          /* non-JSON error body; keep the default */
        }
        setMessages(next)
        setError(msg)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let acc = ''

      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        acc += decoder.decode(value, { stream: true })
        setMessages([...next, { role: 'assistant', content: acc }])
      }

      if (!acc.trim()) {
        setMessages(next)
        setError('The advisor returned an empty response. Try rephrasing.')
      }
    } catch {
      setMessages(next)
      setError('Lost connection to the advisor. Check your network and try again.')
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl">
        {tool.name}
      </h1>
      <p className="mt-3 max-w-2xl text-ink-600 dark:text-ink-300">{tool.blurb}</p>

      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 dark:border-amber-500/30 dark:bg-amber-500/10">
        <p className="text-sm leading-relaxed text-amber-900 dark:text-amber-200">
          <strong className="font-bold">It explains, it does not advise.</strong> It will not tell
          you what to buy or sell, what to do with your money, or where a price is going. Ask it how
          something works and it is genuinely useful; ask it what to do and it will decline and
          teach you the reasoning instead.
        </p>
      </div>

      <Panel className="mt-6">
        <div className="min-h-[18rem] space-y-5">
          {messages.length === 0 && !error && (
            <div>
              <p className="text-ink-500 dark:text-ink-400">
                Ask anything about the course or about how markets work.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {STARTERS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => send(s)}
                    className="rounded-full border border-ink-200 px-3.5 py-1.5 text-sm text-ink-600 transition hover:border-emerald-400 hover:text-ink-900 dark:border-ink-700 dark:text-ink-400 dark:hover:text-white"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'flex justify-end' : ''}>
              <div
                className={
                  m.role === 'user'
                    ? 'max-w-[85%] rounded-2xl rounded-br-sm bg-emerald-600 px-4 py-2.5 text-white'
                    : 'max-w-full whitespace-pre-wrap leading-relaxed text-ink-800 dark:text-ink-200'
                }
              >
                {m.content ||
                  (streaming && i === messages.length - 1 ? (
                    <span className="inline-flex gap-1" aria-label="Thinking">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-ink-400 [animation-delay:-0.3s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-ink-400 [animation-delay:-0.15s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-ink-400" />
                    </span>
                  ) : null)}
              </div>
            </div>
          ))}

          {error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
              {error}
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(draft)
          }}
          className="mt-5 flex gap-2 border-t border-ink-200 pt-5 dark:border-ink-800"
        >
          <label className="sr-only" htmlFor="ask">
            Your question
          </label>
          <input
            id="ask"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            disabled={streaming}
            placeholder="Ask about anything in the course…"
            className="min-w-0 flex-1 rounded-lg border border-ink-200 bg-white px-4 py-2.5 text-ink-900 placeholder:text-ink-400 focus:border-emerald-500 disabled:opacity-60 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-100"
          />
          <button type="submit" disabled={streaming || !draft.trim()} className="btn-primary">
            {streaming ? 'Thinking…' : 'Ask'}
            {!streaming && <ArrowRightIcon className="h-4 w-4" />}
          </button>
        </form>

        {messages.length > 0 && (
          <button
            type="button"
            onClick={() => {
              setMessages([])
              setError(null)
            }}
            className="mt-3 text-sm text-ink-400 hover:text-ink-700 dark:hover:text-ink-200"
          >
            Clear conversation
          </button>
        )}
      </Panel>

      <p className="mt-4 text-xs leading-relaxed text-ink-400 dark:text-ink-500">
        Conversations are sent to OpenAI's API to generate a reply and are not stored by this
        site. Answers can be wrong or out of date, and none of it is financial advice.
      </p>
    </div>
  )
}
