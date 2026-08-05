import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { ALL_MODULES, TRACKS } from '../data/curriculum.js'
import { DEFAULT_STATUS, STATUSES } from '../data/statuses.js'

const STORAGE_KEY = 'stockguide:progress:v2'
const LEGACY_KEY = 'stockguide:progress:v1'

/**
 * Shape of the persisted blob:
 *
 *   {
 *     status:  { "beginner/what-is-a-stock": "complete" },
 *     touched: { "beginner/what-is-a-stock": "2026-08-04T12:00:00.000Z" },
 *     quizzes: { "beginner/what-is-a-stock": { correct: 4, total: 5, at: "..." } }
 *   }
 *
 * Keyed by the module's global id (`track/slug`) so renaming a track can never
 * silently merge two modules' progress together.
 */
const EMPTY = { status: {}, touched: {}, quizzes: {} }

function readLegacy() {
  // v1 stored a binary { completed: { id: date } }. Anyone who used the site
  // before the status control existed keeps their progress.
  try {
    const raw = localStorage.getItem(LEGACY_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed?.completed) return null
    const status = {}
    for (const id of Object.keys(parsed.completed)) status[id] = 'complete'
    return { status, touched: { ...parsed.completed }, quizzes: parsed.quizzes ?? {} }
  } catch {
    return null
  }
}

function read() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return readLegacy() ?? EMPTY
    const parsed = JSON.parse(raw)
    const status = {}
    // Drop unknown status values rather than letting them poison the UI.
    for (const [id, value] of Object.entries(parsed?.status ?? {})) {
      if (STATUSES[value]) status[id] = value
    }
    return {
      status,
      touched: parsed?.touched && typeof parsed.touched === 'object' ? parsed.touched : {},
      quizzes: parsed?.quizzes && typeof parsed.quizzes === 'object' ? parsed.quizzes : {},
    }
  } catch {
    // Corrupt or unavailable storage should never take the whole site down.
    return EMPTY
  }
}

const ProgressContext = createContext(null)

export function ProgressProvider({ children }) {
  const [state, setState] = useState(read)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch {
      // Storage full or blocked, progress just won't survive a refresh.
    }
  }, [state])

  // Keep multiple open tabs consistent with each other.
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === STORAGE_KEY) setState(read())
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const getStatus = useCallback(
    (moduleId) => state.status[moduleId] ?? DEFAULT_STATUS,
    [state.status]
  )

  const setStatus = useCallback((moduleId, next) => {
    setState((prev) => {
      const status = { ...prev.status }
      const touched = { ...prev.touched }
      if (!next || next === DEFAULT_STATUS) {
        delete status[moduleId]
        delete touched[moduleId]
      } else {
        status[moduleId] = next
        touched[moduleId] = new Date().toISOString()
      }
      return { ...prev, status, touched }
    })
  }, [])

  const isComplete = useCallback(
    (moduleId) => state.status[moduleId] === 'complete',
    [state.status]
  )

  /** Bottom-of-lesson button: flips between complete and cleared. */
  const toggleComplete = useCallback(
    (moduleId) => {
      setStatus(moduleId, state.status[moduleId] === 'complete' ? DEFAULT_STATUS : 'complete')
    },
    [setStatus, state.status]
  )

  const recordQuiz = useCallback((moduleId, correct, total) => {
    setState((prev) => ({
      ...prev,
      quizzes: { ...prev.quizzes, [moduleId]: { correct, total, at: new Date().toISOString() } },
    }))
  }, [])

  const getQuiz = useCallback((moduleId) => state.quizzes[moduleId] ?? null, [state.quizzes])

  const resetAll = useCallback(() => setState(EMPTY), [])

  /** Completion counts per track plus a site-wide total, recomputed on change. */
  const stats = useMemo(() => {
    const tally = (modules) => {
      const counts = { 'not-started': 0, reading: 0, practicing: 0, complete: 0, skipped: 0 }
      for (const m of modules) counts[state.status[m.id] ?? DEFAULT_STATUS] += 1
      const done = counts.complete
      // Started = anything the reader has actually opened and marked.
      const started = modules.length - counts['not-started']
      return {
        counts,
        done,
        started,
        total: modules.length,
        percent: modules.length ? Math.round((done / modules.length) * 100) : 0,
      }
    }

    const byTrack = {}
    for (const track of TRACKS) byTrack[track.slug] = tally(track.modules)
    return { byTrack, overall: tally(ALL_MODULES) }
  }, [state.status])

  /**
   * First module in curriculum order the reader hasn't finished with. A lesson
   * marked "skipped" is deliberately passed over, so it isn't suggested again.
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
      nextModule,
    }),
    [getStatus, setStatus, isComplete, toggleComplete, recordQuiz, getQuiz, resetAll, stats, nextModule]
  )

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
}

export function useProgress() {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('useProgress must be used inside <ProgressProvider>')
  return ctx
}
