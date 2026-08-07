/**
 * The FinLit Pro wordmark: "FinLit" in ink, "Pro" in the brand emerald.
 *
 * Kept as one component so the two-tone treatment cannot drift between the
 * navbar, the footer and the homepage hero. Size, weight and tracking come
 * from the caller, because the hero renders this at 7xl and the footer at
 * 14px and they should stay free to differ.
 */
export default function Wordmark({ className = '' }) {
  return (
    <span className={className}>
      <span className="text-ink-900 dark:text-white">FinLit</span>{' '}
      <span className="text-emerald-600 dark:text-emerald-400">Pro</span>
    </span>
  )
}
