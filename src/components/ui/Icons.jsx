/**
 * Inline SVG icon set.
 *
 * Kept local rather than pulling in an icon package: it is a handful of paths,
 * it keeps the bundle small, and there are no external requests to fail.
 * Every icon inherits `currentColor` and takes a className for sizing.
 */

const base = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  viewBox: '0 0 24 24',
  'aria-hidden': true,
}

export const CheckIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M20 6 9 17l-5-5" />
  </svg>
)

export const CheckCircleIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="m8.5 12 2.5 2.5 4.5-5" />
  </svg>
)

export const CircleIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
  </svg>
)

export const ArrowRightIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
)

export const ArrowLeftIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M19 12H5M11 18l-6-6 6-6" />
  </svg>
)

export const ChartIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M3 3v16a2 2 0 0 0 2 2h16" />
    <path d="m7 14 3.5-3.5 3 3L21 7" />
  </svg>
)

export const LightbulbIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M9 18h6M10 22h4" />
    <path d="M12 2a6 6 0 0 0-3.6 10.8c.6.5.9 1.2 1 1.9l.1 1.3h5l.1-1.3c.1-.7.4-1.4 1-1.9A6 6 0 0 0 12 2Z" />
  </svg>
)

export const AlertIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M12 9v4M12 17h.01" />
    <path d="M10.3 3.9 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
  </svg>
)

export const BookIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
  </svg>
)

export const WrenchIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M14.7 6.3a4 4 0 0 0 5 5l-9.9 9.9a2.1 2.1 0 0 1-3-3l9.9-9.9a4 4 0 0 0-2-2Z" />
  </svg>
)

export const ClockIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </svg>
)

export const SunIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </svg>
)

export const MoonIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
  </svg>
)

export const MenuIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M4 6h16M4 12h16M4 18h16" />
  </svg>
)

export const CloseIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M18 6 6 18M6 6l12 12" />
  </svg>
)

export const XCircleIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="m15 9-6 6M9 9l6 6" />
  </svg>
)

export const RefreshIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M21 12a9 9 0 1 1-2.6-6.4" />
    <path d="M21 3v6h-6" />
  </svg>
)

export const SearchIcon = (p) => (
  <svg {...base} {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.5-3.5" />
  </svg>
)

export const ScaleIcon = (p) => (
  <svg {...base} {...p}>
    <path d="M12 3v18M7 21h10M5 7h14M5 7l-3 6a3 3 0 0 0 6 0L5 7ZM19 7l-3 6a3 3 0 0 0 6 0l-3-6Z" />
  </svg>
)
