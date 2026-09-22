/**
 * Per-route search metadata: title, description, canonical URL and robots.
 *
 * One source, three consumers, which is the whole point:
 *
 *   scripts/prerender.mjs          writes it into a static HTML file for every
 *                                  route at build time, so a crawler reading
 *                                  raw HTML gets the right page identity
 *                                  without running any JavaScript;
 *   scripts/generate-sitemap.mjs   lists the indexable routes from it;
 *   components/layout/RouteHead    applies it in the browser on every
 *                                  client-side navigation.
 *
 * Before this existed every URL shipped index.html's head unchanged. All 46
 * pages shared one title, and every lesson declared the HOMEPAGE as its
 * canonical URL, which is an explicit instruction to search engines to treat
 * each lesson as a duplicate of the homepage and index that instead.
 *
 * Deliberately free of JSX and of imports outside src/data, so plain Node can
 * load it at build time.
 *
 * Tracks, lessons and simulator tools are derived from their data files and
 * appear here automatically. A new top-level page (like /glossary) needs a
 * case in getRouteMeta and an entry in listIndexableRoutes.
 */
import { TRACKS, getModule, getNeighbours, getTrack } from './curriculum.js'
import { TOOLS, getTool } from './simulator.js'
import { GLOSSARY_LIST } from './glossary.js'

export const SITE_ORIGIN = 'https://www.finlitpro.org'
export const SITE_NAME = 'FinLit Pro'

const INDEX = 'index, follow, max-image-preview:large'
const NOINDEX = 'noindex, follow'

/** Search results cut descriptions off at roughly this many characters. */
export const DESCRIPTION_MAX = 160

/** Absolute URL for a site path. */
export const absoluteUrl = (path) => `${SITE_ORIGIN}${path}`

/** Drop a trailing slash, query and hash, so `/beginner/` and `/beginner` agree. */
export function normalisePath(pathname = '/') {
  const bare = String(pathname).split(/[?#]/)[0] || '/'
  return bare.length > 1 ? bare.replace(/\/+$/, '') || '/' : '/'
}

/** Ensure a blurb reads as a sentence before more text is appended to it. */
const sentence = (text) => {
  const t = String(text).trim()
  return /[.!?]$/.test(t) ? t : `${t}.`
}

/**
 * Keep a description inside what a results page will show. Cuts at a word
 * boundary rather than mid-word, so a long blurb degrades into a clean
 * truncation instead of a broken one.
 */
function fit(text, max = DESCRIPTION_MAX) {
  const t = String(text).replace(/\s+/g, ' ').trim()
  if (t.length <= max) return t
  const cut = t.slice(0, max - 1)
  return `${cut.slice(0, cut.lastIndexOf(' ')).replace(/[,;:.]$/, '')}…`
}

/** Results pages show roughly this many characters of a title. */
export const TITLE_MAX = 65

/**
 * The longest of the candidate titles that still fits, so a short lesson
 * title keeps its track name and brand while a long one sheds them rather
 * than being cut off mid-word by the results page.
 */
function titleFrom(...candidates) {
  return candidates.find((t) => t.length <= TITLE_MAX) ?? candidates[candidates.length - 1]
}

/**
 * Append context to a description only when it fits whole. A suffix cut in
 * half ("A free 11-minute lesson in the…") reads worse than no suffix at all.
 */
function withSuffix(base, ...suffixes) {
  const b = sentence(base)
  for (const s of suffixes) if (`${b} ${s}`.length <= DESCRIPTION_MAX) return `${b} ${s}`
  return b
}

function page({ path, title, description, robots = INDEX, h1, intro, links = [], crumbs = [], terms }) {
  return {
    path,
    url: absoluteUrl(path),
    title,
    description: fit(description),
    robots,
    // A page that asks not to be indexed has no business naming a canonical.
    canonical: robots === INDEX ? absoluteUrl(path) : null,
    indexable: robots === INDEX,
    h1,
    intro,
    links,
    crumbs,
    terms,
  }
}

const HOME = { name: 'Home', path: '/' }

// ---------------------------------------------------------------------------

function home() {
  return page({
    path: '/',
    title: 'FinLit Pro: Learn the Stock Market, Beginner to Advanced (Free)',
    description:
      'A free stock market course for students: how shares work, stable versus risky stocks, real chart case studies and options, with quizzes and simulators.',
    h1: SITE_NAME,
    intro:
      'A free collection of structured, honest lessons to take you from your first share to understanding real risk.',
    links: [
      ...TRACKS.map((t) => ({ href: t.path, label: `${t.name}: ${t.title}` })),
      { href: '/simulator', label: 'Simulator: run the numbers yourself' },
      { href: '/glossary', label: 'Glossary of investing terms' },
    ],
  })
}

function glossary() {
  const n = GLOSSARY_LIST.length
  return page({
    path: '/glossary',
    title: `Stock Market Glossary: ${n} Terms Explained | ${SITE_NAME}`,
    description: `Plain-English definitions of ${n} investing terms, from share and dividend to beta, P/E ratio and options. Part of ${SITE_NAME}, a free stock market course.`,
    h1: 'Glossary',
    intro: `${n} investing terms, each defined in plain English.`,
    crumbs: [HOME, { name: 'Glossary', path: '/glossary' }],
    terms: GLOSSARY_LIST.map((g) => ({ term: g.term, definition: g.short })),
  })
}

function dashboard() {
  // Rendered entirely from this browser's LocalStorage: there is nothing on it
  // that a search engine could index usefully, and nothing worth ranking.
  return page({
    path: '/dashboard',
    title: `Your Progress | ${SITE_NAME}`,
    description: 'Your lesson progress, quiz scores, activity and streak, saved in this browser.',
    robots: NOINDEX,
    h1: 'Your progress',
  })
}

function simulatorHome() {
  const n = TOOLS.length
  return page({
    path: '/simulator',
    title: `Free Stock Market Simulators and Calculators | ${SITE_NAME}`,
    description: `${n} free tools: live charts with RSI and moving averages, a Monte Carlo projector, options payoff, portfolio beta and compound growth. No sign-up.`,
    h1: 'Run the numbers yourself',
    intro: 'Hands-on tools that sit alongside the course. Nothing here is advice; every number is shown with its working.',
    crumbs: [HOME, { name: 'Simulator', path: '/simulator' }],
    links: TOOLS.map((t) => ({ href: `/simulator/${t.slug}`, label: t.name, note: t.blurb })),
  })
}

function toolPage(tool) {
  const path = `/simulator/${tool.slug}`
  return page({
    path,
    title: `${tool.name}: Free Stock Tool | ${SITE_NAME}`,
    description: `${sentence(tool.blurb)} Free to use, no sign-up.`,
    h1: tool.name,
    intro: tool.blurb,
    crumbs: [HOME, { name: 'Simulator', path: '/simulator' }, { name: tool.name, path }],
    links: [
      ...(tool.lesson ? [{ href: tool.lesson, label: `Related lesson: ${tool.lessonName}` }] : []),
      { href: '/simulator', label: 'All simulator tools' },
    ],
  })
}

function trackPage(track) {
  return page({
    path: track.path,
    title: titleFrom(`${track.name}: ${track.title} | ${SITE_NAME}`, `${track.name}: ${track.title}`),
    description: withSuffix(track.description.length <= DESCRIPTION_MAX ? track.description : track.tagline, `Free ${SITE_NAME} course track, ${track.modules.length} lessons.`, `${track.modules.length} free lessons.`),
    h1: `${track.name}: ${track.title}`,
    intro: track.description,
    crumbs: [HOME, { name: track.name, path: track.path }],
    links: track.modules.map((m) => ({ href: m.path, label: m.title, note: m.blurb })),
  })
}

function lessonPage(mod) {
  const track = getTrack(mod.trackSlug)
  const { prev, next } = getNeighbours(mod.id)
  return page({
    path: mod.path,
    // The track name keeps otherwise similar titles apart, the four recaps in
    // particular, and tells a searcher what level the lesson is pitched at.
    title: titleFrom(
      `${mod.title} | ${track.name} | ${SITE_NAME}`,
      `${mod.title} | ${SITE_NAME}`,
      mod.title
    ),
    description: withSuffix(
      mod.blurb,
      `A free ${mod.minutes}-minute lesson in the ${track.name} track of ${SITE_NAME}.`,
      `A free ${mod.minutes}-minute ${track.name} lesson.`,
      `Free lesson, ${mod.minutes} min.`
    ),
    h1: mod.title,
    intro: mod.blurb,
    crumbs: [HOME, { name: track.name, path: track.path }, { name: mod.title, path: mod.path }],
    links: [
      ...(prev ? [{ href: prev.path, label: `Previous: ${prev.title}` }] : []),
      ...(next ? [{ href: next.path, label: `Next: ${next.title}` }] : []),
      { href: track.path, label: `All ${track.name} lessons` },
    ],
  })
}

/** What an unknown URL says about itself. Never indexed. */
export function notFound(path = '/404') {
  return page({
    path,
    title: `Page Not Found | ${SITE_NAME}`,
    description: 'That page does not exist. Every lesson is reachable from the FinLit Pro homepage.',
    robots: NOINDEX,
    h1: 'Page not found',
    intro: 'That page does not exist. Every lesson is reachable from the homepage.',
    links: [{ href: '/', label: 'Go to the homepage' }],
  })
}

// ---------------------------------------------------------------------------

/**
 * Metadata for any path the app can be asked to render. Mirrors App.jsx's
 * routing, including its fall-through to NotFound for unknown slugs, so the
 * head a crawler sees always agrees with the page a reader sees.
 */
export function getRouteMeta(pathname) {
  const path = normalisePath(pathname)
  if (path === '/') return home()
  if (path === '/glossary') return glossary()
  if (path === '/dashboard') return dashboard()
  if (path === '/simulator') return simulatorHome()

  const parts = path.slice(1).split('/')
  if (parts[0] === 'simulator' && parts.length === 2) {
    const tool = getTool(parts[1])
    return tool ? toolPage(tool) : notFound(path)
  }
  if (parts.length === 1) {
    const track = getTrack(parts[0])
    return track ? trackPage(track) : notFound(path)
  }
  if (parts.length === 2) {
    const mod = getModule(parts[0], parts[1])
    return mod ? lessonPage(mod) : notFound(path)
  }
  return notFound(path)
}

/** Every route that should appear in search, in recommended reading order. */
export function listIndexableRoutes() {
  return [
    '/',
    ...TRACKS.flatMap((t) => [t.path, ...t.modules.map((m) => m.path)]),
    '/simulator',
    ...TOOLS.map((t) => `/simulator/${t.slug}`),
    '/glossary',
  ]
}

/** Every route that gets its own static HTML file at build time. */
export function listPrerenderRoutes() {
  return [...listIndexableRoutes(), '/dashboard']
}

/** schema.org BreadcrumbList for a page, or null if it has no trail. */
export function breadcrumbJsonLd(meta) {
  if (!meta.crumbs?.length) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: meta.crumbs.map((c, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: c.name,
      item: absoluteUrl(c.path),
    })),
  }
}
