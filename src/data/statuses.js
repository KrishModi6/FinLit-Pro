/**
 * Per-module progress states, modelled on USACO Guide's module status control.
 *
 * A binary done/not-done is too coarse for a course people dip in and out of:
 * "I read it but haven't practised" and "I deliberately skipped this" are real,
 * different states, and both are useful to see in the sidebar at a glance.
 *
 * Only `complete` counts toward the percentage. `skipped` is tracked separately
 * so a reader who genuinely doesn't need a lesson isn't nagged by it forever.
 */
export const STATUSES = {
  'not-started': {
    id: 'not-started',
    label: 'Not Started',
    dot: 'bg-ink-300 dark:bg-ink-600',
    text: 'text-ink-500 dark:text-ink-400',
    chip: 'border-ink-200 text-ink-600 dark:border-ink-700 dark:text-ink-300',
  },
  reading: {
    id: 'reading',
    label: 'Reading',
    dot: 'bg-amber-400',
    text: 'text-amber-700 dark:text-amber-400',
    chip: 'border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-300',
  },
  practicing: {
    id: 'practicing',
    label: 'Practicing',
    dot: 'bg-orange-500',
    text: 'text-orange-700 dark:text-orange-400',
    chip: 'border-orange-300 bg-orange-50 text-orange-800 dark:border-orange-500/40 dark:bg-orange-500/10 dark:text-orange-300',
  },
  complete: {
    id: 'complete',
    label: 'Complete',
    dot: 'bg-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-400',
    chip: 'border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-300',
  },
  skipped: {
    id: 'skipped',
    label: 'Skipped',
    dot: 'bg-sky-400',
    text: 'text-sky-700 dark:text-sky-400',
    chip: 'border-sky-300 bg-sky-50 text-sky-800 dark:border-sky-500/40 dark:bg-sky-500/10 dark:text-sky-300',
  },
}

/** Display order in the status dropdown. */
export const STATUS_ORDER = ['not-started', 'reading', 'practicing', 'complete', 'skipped']

export const DEFAULT_STATUS = 'not-started'

export function getStatusMeta(id) {
  return STATUSES[id] ?? STATUSES[DEFAULT_STATUS]
}
