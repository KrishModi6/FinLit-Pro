import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { ALL_MODULES, TRACKS } from '../data/curriculum.js'
import { DEFAULT_STATUS, STATUSES } from '../data/statuses.js'

const STORAGE_KEY = 'stockguide:progress:v3'
const LEGACY_KEYS = ['stockguide:progress:v2', 'stockguide:progress:v1']

/**
 * Shape of the persisted blob:
 *
 *   {
 *     status:   { "beginner/what-is-a-stock": "complete" },
 *     touched:  { "beginner/what-is-a-stock": "2026-08-04T12:00:00.000Z" },
 *     quizzes:  { "beginner/what-is-a-stock": { correct: 4, total: 5, at: "..." } },
 *     activity: { "2026-08-04": 3 },     // things done that day
 *     visits:   { "2026-08-04": true }   // days the site was opened
 *   }
 *
 * Keyed by the module's global id (`track/slug`) so renaming a track can never
 * silently merge two modules' progress together.
 */
const EMPTY = { status: {}, touched: {}, quizzes: {}, activity: {}, visits: {} }

/** Local calendar day, not UTC. A day should end when the reader's day ends. */
export function dayKey(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function migrate(parsed) {
  if (!parsed || typeof parsed !== 'object') return null

  // v1 stored a binary { completed: { id: date } }.
  if (parsed.completed && !parsed.status) {
    const status = {}
    for (const id of Object.keys(parsed.completed)) status[id] = 'complete'
    return { ...EMPTY, status, touched: { ...parsed.completed }, quizzes: parsed.quizzes ?? {} }
  }

  const status = {}
  for (const [id, value] of Object.entries(parsed.status ?? {})) {
    if (STATUSES[value]) status[id] = value // drop unknown values rather than poison the UI
  }

  const activity = {}
  for (const [day, n] of Object.entries(parsed.activity ?? {})) {
    if (Number.isFinite(Number(n))) activity[day] = Number(n)
  }

  return {
    status,
    touched: parsed.touched && typeof parsed.touched === 'object' ? parsed.touched : {},
    quizzes: parsed.quizzes && typeof parsed.quizzes === 'object' ? parsed.quizzes : {},
    activity,
    visits: parsed.visits && typeof parsed.visits === 'object' ? parsed.visits : {},
  }
}

function read() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return migrate(JSON.parse(raw)) ?? EMPTY
    for (const key of LEGACY_KEYS) {
      const old = localStorage.getItem(key)
      if (old) return migrate(JSON.parse(old)) ?? EMPTY
    }
    return EMPTY
  } catch {
    // Corrupt or unavailable storage should never take the whole site down.
    return EMPTY
  }
}

/** Consecutive days ending today (or yesterday, if today is not logged yet). */
function computeStreak(visits) {
  const days = new Set(Object.keys(visits))
  if (!days.size) return { current: 0, longest: 0 }

  const cursor = new Date()
  cursor.setHours(0, 0, 0, 0)
  if (!days.has(dayKey(cursor))) cursor.setDate(cursor.getDate() - 1)

  let current = 0
  while (days.has(dayKey(cursor))) {
    current++
    cursor.setDate(cursor.getDate() - 1)
  }

  // Longest run anywhere in the history.
  const sorted = [...days].sort()
  let longest = 0
  let run = 0
  let prev = null
  for (const d of sorted) {
    const date = new Date(`${d}T00:00:00`)
    if (prev && (date - prev) / 86400000 === 1) run++
    else run = 1
    if (run > longest) longest = run
    prev = date
  }

  return { current, longest: Math.max(longest, current) }
}

const ProgressContext = createContext(null)

export function ProgressProvider({ children }) {
  const [state, setState] = useState(read)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage full or blocked; progress just will not survive a refresh.
    }
  }, [state])

  // Log today's visit exactly once per session mount.
  useEffect(() => {
    const today = dayKey()
    setState((prev) => (prev.visits[today] ? prev : { ...prev, visits: { ...prev.visits, [today]: true } }))
  }, [])

  // Keep multiple open tabs consistent with each other.
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === STORAGE_KEY) setState(read())
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  /** Bump today's activity counter. */
  const bump = (prev, by = 1) => {
    const today = dayKey()
    return { ...prev, activity: { ...prev.activity, [today]: (prev.activity[today] ?? 0) + by } }
  }

  const getStatus = useCallback((moduleId) => state.status[moduleId] ?? DEFAULT_STATUS, [state.status])

  const setStatus = useCallback((moduleId, next) => {
    setState((prev) => {
      const status = { ...prev.status }
      const touched = { ...prev.touched }
      if (!next || next === DEFAULT_STATUS) {
        delete status[moduleId]
        delete touched[moduleId]
        return { ...prev, status, touched }
      }
      status[moduleId] = next
      touched[moduleId] = new Date().toISOString()
      return bump({ ...prev, status, touched })
    })
  }, [])

  const isComplete = useCallback((moduleId) => state.status[moduleId] === 'complete', [state.status])

  /** Bottom-of-lesson button: flips between complete and cleared. */
  const toggleComplete = useCallback(
    (moduleId) => {
      setStatus(moduleId, state.status[moduleId] === 'complete' ? DEFAULT_STATUS : 'complete')
    },
    [setStatus, state.status]
  )

  const recordQuiz = useCallback((moduleId, correct, total) => {
    setState((prev) =>
      bump({
        ...prev,
        quizzes: { ...prev.quizzes, [moduleId]: { correct, total, at: new Date().toISOString() } },
      })
    )
  }, [])

  const getQuiz = useCallback((moduleId) => state.quizzes[moduleId] ?? null, [state.quizzes])

  const resetAll = useCallback(() => setState({ ...EMPTY, visits: { [dayKey()]: true } }), [])

  /** Completion counts per track plus a site-wide total, recomputed on change. */
  const stats = useMemo(() => {
    const tally = (modules) => {
      const counts = { 'not-started': 0, reading: 0, practicing: 0, complete: 0, skipped: 0 }
      for (const m of modules) counts[state.status[m.id] ?? DEFAULT_STATUS] += 1
      return {
        counts,
        done: counts.complete,
        inProgress: counts.reading + counts.practicing,
        started: modules.length - counts['not-started'],
        total: modules.length,
        percent: modules.length ? Math.round((counts.complete / modules.length) * 100) : 0,
      }
    }

    const byTrack = {}
    for (const track of TRACKS) byTrack[track.slug] = tally(track.modules)
    return { byTrack, overall: tally(ALL_MODULES) }
  }, [state.status])

  /** Quiz attempt counts, for the second statistics card. */
  const quizStats = useMemo(() => {
    let passed = 0
    let attempted = 0
    for (const m of ALL_MODULES) {
      const q = state.quizzes[m.id]
      if (!q) continue
      if (q.correct / q.total >= 0.6) passed++
      else attempted++
    }
    const skipped = ALL_MODULES.filter(
      (m) => state.status[m.id] === 'skipped' && !state.quizzes[m.id]
    ).length
    return {
      passed,
      attempted,
      skipped,
      notStarted: ALL_MODULES.length - passed - attempted - skipped,
      total: ALL_MODULES.length,
    }
  }, [state.quizzes, state.status])

  const streak = useMemo(() => computeStreak(state.visits), [state.visits])

  const activity = state.activity

  /**
   * First module in curriculum order the reader has not finished with. A lesson
   * marked "skipped" is deliberately passed over, so it is not suggested again.
   */
  const nextModule = useMemo(() => {
    const settled = new Set(['complete', 'skipped'])
    return ALL_MODULES.find((m) => !settled.has(state.status[m.id] ?? DEFAULT_STATUS)) ?? null
  }, [state.status])

  const value = useMemo(
    () => ({
      getStatus,
      setStatus,
      isComplete,
      toggleComplete,
      recordQuiz,
      getQuiz,
      resetAll,
      stats,
      quizStats,
      streak,
      activity,
      nextModule,
    }),
    [
      getStatus,
      setStatus,
      isComplete,
      toggleComplete,
      recordQuiz,
      getQuiz,
      resetAll,
      stats,
      quizStats,
      streak,
      activity,
      nextModule,
    ]
  )

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
}

export function useProgress() {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('useProgress must be used inside <ProgressProvider>')
  return ctx
}
