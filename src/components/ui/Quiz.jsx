import { useEffect, useMemo, useState } from 'react'
import { CheckCircleIcon, RefreshIcon, XCircleIcon } from './Icons.jsx'
import { useProgress } from '../../context/ProgressContext.jsx'

/**
 * End-of-module quiz with instant feedback.
 *
 * Questions are plain objects:
 *
 *   { prompt: 'What is a share?', options: ['a', 'b'], answer: 1, explanation: '…' }
 *   { prompt: 'Dividends are guaranteed.', type: 'tf', answer: false, explanation: '…' }
 *
 * A question locks as soon as it is answered. The point is to find out whether
 * you knew it, not to let you click until something goes green. "Start over"
 * clears the lock if you want a genuine second run.
 */
function normalise(q) {
  if (q.type === 'tf') {
    return {
      ...q,
      options: ['True', 'False'],
      // `answer: true` means the statement is true, i.e. option index 0.
      answerIndex: q.answer === true || q.answer === 0 ? 0 : 1,
    }
  }
  return { ...q, answerIndex: q.answer }
}

export default function Quiz({ moduleId, questions }) {
  const items = useMemo(() => questions.map(normalise), [questions])
  const { recordQuiz, getQuiz } = useProgress()

  // answers[i] = index the reader picked, or undefined if unanswered.
  const [answers, setAnswers] = useState({})

  const answeredCount = Object.keys(answers).length
  const correctCount = items.reduce((n, q, i) => n + (answers[i] === q.answerIndex ? 1 : 0), 0)
  const finished = answeredCount === items.length

  const previous = getQuiz(moduleId)

  // Persist the score once every question has been attempted.
  useEffect(() => {
    if (finished) recordQuiz(moduleId, correctCount, items.length)
  }, [finished, correctCount, items.length, moduleId, recordQuiz])

  // Wipe local answers when navigating to a different module.
  useEffect(() => setAnswers({}), [moduleId])

  const choose = (qIndex, optIndex) => {
    if (answers[qIndex] !== undefined) return // locked
    setAnswers((prev) => ({ ...prev, [qIndex]: optIndex }))
  }

  return (
    <section
      id="quiz"
      aria-labelledby="quiz-heading"
      className="mt-14 scroll-mt-24 rounded-2xl border border-ink-200 bg-ink-50/60 p-5 dark:border-ink-800 dark:bg-ink-900/40 sm:p-7"
    >
      <header className="flex flex-wrap items-baseline justify-between gap-3">
        <div>
          <h2 id="quiz-heading" className="!mt-0 text-xl font-bold text-ink-900 dark:text-white">
            Check yourself
          </h2>
          <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">
            {items.length} questions. You get one shot at each. That is the whole point.
          </p>
        </div>

        <div className="text-right">
          <span className="text-sm font-semibold tabular-nums text-ink-600 dark:text-ink-300">
            {answeredCount} / {items.length} answered
          </span>
          {previous && !finished && (
            <span className="mt-0.5 block text-xs text-ink-400 dark:text-ink-500">
              Last time: {previous.correct}/{previous.total}
            </span>
          )}
        </div>
      </header>

      {/* `list-none pl-0` overrides the `.lesson ol` defaults, the quiz renders
          its own question numbers, so the decimal markers would double up. */}
      <ol className="mt-6 list-none space-y-7 pl-0">
        {items.map((q, qi) => {
          const picked = answers[qi]
          const locked = picked !== undefined
          const gotIt = picked === q.answerIndex

          return (
            <li key={qi}>
              <p className="flex gap-2.5 font-semibold text-ink-900 dark:text-ink-100">
                <span className="shrink-0 tabular-nums text-ink-400 dark:text-ink-500">{qi + 1}.</span>
                <span>{q.prompt}</span>
              </p>

              <div className="mt-3 space-y-2 pl-7">
                {q.options.map((opt, oi) => {
                  const isAnswer = oi === q.answerIndex
                  const isPicked = picked === oi

                  // Once locked: highlight the right answer green, and the
                  // reader's wrong pick red. Everything else fades back.
                  let tone =
                    'border-ink-200 bg-white hover:border-ink-400 dark:border-ink-700 dark:bg-ink-900 dark:hover:border-ink-500'
                  if (locked && isAnswer)
                    tone = 'border-emerald-500 bg-emerald-50 dark:border-emerald-500 dark:bg-emerald-500/15'
                  else if (locked && isPicked)
                    tone = 'border-rose-500 bg-rose-50 dark:border-rose-500 dark:bg-rose-500/15'
                  else if (locked) tone = 'border-ink-200 bg-white opacity-55 dark:border-ink-800 dark:bg-ink-900'

                  return (
                    <button
                      key={oi}
                      type="button"
                      disabled={locked}
                      onClick={() => choose(qi, oi)}
                      className={`flex w-full items-start gap-3 rounded-lg border px-4 py-2.5 text-left text-[0.95rem] transition disabled:cursor-default ${tone}`}
                    >
                      <span className="mt-0.5 shrink-0 font-mono text-xs font-bold text-ink-400 dark:text-ink-500">
                        {String.fromCharCode(65 + oi)}
                      </span>
                      <span className="flex-1 text-ink-800 dark:text-ink-200">{opt}</span>
                      {locked && isAnswer && (
                        <CheckCircleIcon className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
                      )}
                      {locked && isPicked && !isAnswer && (
                        <XCircleIcon className="mt-0.5 h-5 w-5 shrink-0 text-rose-600 dark:text-rose-400" />
                      )}
                    </button>
                  )
                })}
              </div>

              {locked && (
                <div
                  className={`ml-7 mt-3 rounded-lg border-l-4 px-4 py-3 text-[0.9rem] leading-relaxed ${
                    gotIt
                      ? 'border-emerald-500 bg-emerald-50/70 text-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-200'
                      : 'border-rose-500 bg-rose-50/70 text-rose-900 dark:bg-rose-500/10 dark:text-rose-200'
                  }`}
                >
                  <strong className="font-bold">{gotIt ? 'Correct. ' : 'Not quite. '}</strong>
                  {q.explanation}
                </div>
              )}
            </li>
          )
        })}
      </ol>

      {finished && (
        <div className="mt-7 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-ink-200 bg-white px-5 py-4 dark:border-ink-700 dark:bg-ink-900">
          <div>
            <p className="text-lg font-bold text-ink-900 dark:text-white">
              {correctCount} out of {items.length}
            </p>
            <p className="mt-0.5 text-sm text-ink-500 dark:text-ink-400">
              {correctCount === items.length
                ? 'Clean sweep. Move on to the next lesson.'
                : correctCount >= Math.ceil(items.length * 0.6)
                  ? 'Solid. Re-read the sections behind anything you missed.'
                  : 'Worth another pass through the lesson before you continue.'}
            </p>
          </div>
          <button type="button" onClick={() => setAnswers({})} className="btn-secondary">
            <RefreshIcon className="h-4 w-4" />
            Start over
          </button>
        </div>
      )}
    </section>
  )
}
