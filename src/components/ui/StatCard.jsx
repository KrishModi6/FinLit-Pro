/**
 * A statistics card: four counted states as coloured discs, over a single
 * segmented bar showing their proportions.
 *
 * `items` is [{ label, value, disc, bar }] where `disc` and `bar` are Tailwind
 * class strings written out in full so the JIT compiler can see them.
 */
export default function StatCard({ title, items, total }) {
  const sum = total ?? items.reduce((s, i) => s + i.value, 0)

  return (
    <section className="rounded-2xl border border-ink-200 bg-white p-5 dark:border-ink-800 dark:bg-ink-900/40 sm:p-6">
      <h3 className="text-base font-semibold text-ink-900 dark:text-white">{title}</h3>

      <dl className="mt-5 grid grid-cols-4 gap-2">
        {items.map((item) => (
          <div key={item.label} className="flex flex-col items-center text-center">
            <dd
              className={`flex h-14 w-14 items-center justify-center rounded-full text-xl font-bold tabular-nums sm:h-16 sm:w-16 sm:text-2xl ${item.disc}`}
            >
              {item.value}
            </dd>
            <dt className="mt-2 text-[0.6875rem] font-semibold uppercase tracking-wide text-ink-500 dark:text-ink-400">
              {item.label}
            </dt>
          </div>
        ))}
      </dl>

      <div
        className="mt-6 flex h-2.5 w-full overflow-hidden rounded-full bg-ink-200 dark:bg-ink-800"
        role="img"
        aria-label={items.map((i) => `${i.value} ${i.label}`).join(', ')}
      >
        {items.map((item) =>
          item.value > 0 && sum > 0 ? (
            <span
              key={item.label}
              className={item.bar}
              style={{ width: `${(item.value / sum) * 100}%` }}
              title={`${item.label}: ${item.value}`}
            />
          ) : null
        )}
      </div>

      <p className="mt-2 text-right text-sm text-ink-500 dark:text-ink-400">{sum} total</p>
    </section>
  )
}
