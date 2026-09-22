/**
 * Writes a static HTML file for every route, after `vite build`.
 *
 * The site is a single-page app, so before this every URL was served the same
 * index.html: one title, one description, an empty body, and a canonical tag
 * pointing at the homepage. That last part actively told search engines that
 * every lesson was a duplicate of the homepage.
 *
 * Now each route gets dist/<route>/index.html carrying its own title,
 * description, canonical, robots and share tags, a BreadcrumbList, and a short
 * static body: its heading, a summary and links onward. Crawlers that read raw
 * HTML get the page's real identity and a crawlable link graph without
 * running JavaScript, and a reader on a slow connection sees the page title
 * and summary instead of a blank screen while the app loads. React then
 * mounts over #root and renders the full page as before.
 *
 * All values come from src/data/seo.js, which the running app also reads, so
 * the static head and the live head cannot disagree.
 *
 * Fails the build loudly if the template markers it relies on go missing,
 * because a silent no-op here would ship 46 identical pages again.
 */
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  breadcrumbJsonLd,
  getRouteMeta,
  listPrerenderRoutes,
  notFound,
} from '../src/data/seo.js'

const here = dirname(fileURLToPath(import.meta.url))
const dist = resolve(here, '../dist')
const template = readFileSync(join(dist, 'index.html'), 'utf8')

const esc = (s) =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

/** Replace the text between two markers, or stop the build if they are gone. */
function between(html, start, end, replacement) {
  const a = html.indexOf(start)
  const b = html.indexOf(end)
  if (a === -1 || b === -1 || b < a) {
    throw new Error(`prerender: markers ${start} / ${end} not found in dist/index.html`)
  }
  return html.slice(0, a + start.length) + replacement + html.slice(b)
}

function headFor(meta) {
  const tags = [
    `<title>${esc(meta.title)}</title>`,
    `<meta name="description" content="${esc(meta.description)}" />`,
    `<meta name="robots" content="${esc(meta.robots)}" />`,
    meta.canonical ? `<link rel="canonical" href="${esc(meta.canonical)}" />` : null,
    `<meta property="og:title" content="${esc(meta.title)}" />`,
    `<meta property="og:description" content="${esc(meta.description)}" />`,
    `<meta property="og:url" content="${esc(meta.url)}" />`,
    `<meta name="twitter:title" content="${esc(meta.title)}" />`,
    `<meta name="twitter:description" content="${esc(meta.description)}" />`,
  ].filter(Boolean)
  return `\n    ${tags.join('\n    ')}\n    `
}

/**
 * Only classes the app already uses, because Tailwind only ships classes it
 * finds in src/. A class invented here would silently render unstyled.
 */
const C = {
  wrap: 'mx-auto max-w-3xl px-4 py-10 sm:px-6 sm:py-14',
  crumbs: 'text-sm text-ink-500 dark:text-ink-400',
  h1: 'mt-2 text-3xl font-extrabold tracking-tight text-ink-900 dark:text-white sm:text-4xl',
  intro: 'mt-3 text-ink-600 dark:text-ink-300',
  list: 'mt-6 space-y-2',
  link: 'font-semibold text-emerald-700 hover:underline dark:text-emerald-400',
  note: 'text-sm text-ink-500 dark:text-ink-400',
}

function bodyFor(meta) {
  const crumbs = meta.crumbs.length
    ? `<nav aria-label="Breadcrumb" class="${C.crumbs}">${meta.crumbs
        .map((c, i) =>
          i === meta.crumbs.length - 1 ? esc(c.name) : `<a href="${esc(c.path)}">${esc(c.name)}</a> / `
        )
        .join('')}</nav>`
    : ''
  const intro = meta.intro ? `<p class="${C.intro}">${esc(meta.intro)}</p>` : ''
  const links = meta.links.length
    ? `<ul class="${C.list}">${meta.links
        .map(
          (l) =>
            `<li><a class="${C.link}" href="${esc(l.href)}">${esc(l.label)}</a>${
              l.note ? ` <span class="${C.note}">${esc(l.note)}</span>` : ''
            }</li>`
        )
        .join('')}</ul>`
    : ''
  const terms = meta.terms?.length
    ? `<dl class="${C.list}">${meta.terms
        .map((t) => `<dt class="font-semibold">${esc(t.term)}</dt><dd class="${C.note}">${esc(t.definition)}</dd>`)
        .join('')}</dl>`
    : ''
  return `<main class="${C.wrap}">${crumbs}<h1 class="${C.h1}">${esc(meta.h1)}</h1>${intro}${links}${terms}</main>`
}

function render(meta, { isHome }) {
  let html = between(template, '<!--seo:start-->', '<!--seo:end-->', headFor(meta))
  // The homepage keeps the Course description of the whole site. Every other
  // page gets a breadcrumb trail instead, rather than repeating a Course whose
  // URL is the homepage on 45 pages that are not the homepage.
  if (!isHome) {
    const crumbs = breadcrumbJsonLd(meta)
    html = between(
      html,
      '<!--ld:start-->',
      '<!--ld:end-->',
      crumbs ? `\n    <script type="application/ld+json">${JSON.stringify(crumbs)}</script>\n    ` : '\n    '
    )
  }
  if (!html.includes('<div id="root"></div>')) {
    throw new Error('prerender: <div id="root"></div> not found in dist/index.html')
  }
  return html.replace('<div id="root"></div>', `<div id="root">${bodyFor(meta)}</div>`)
}

function write(relPath, html) {
  const file = join(dist, relPath)
  mkdirSync(dirname(file), { recursive: true })
  writeFileSync(file, html, 'utf8')
}

// ---------------------------------------------------------------------------

const routes = listPrerenderRoutes()
for (const route of routes) {
  const meta = getRouteMeta(route)
  const isHome = route === '/'
  write(isHome ? 'index.html' : join(route.slice(1), 'index.html'), render(meta, { isHome }))
}

// Served by Vercel with a real 404 status for any path without a file above.
// It still boots the app, which renders the not-found page and links home.
write('404.html', render(notFound('/404'), { isHome: false }))

// Guard against the classes above not existing in the built stylesheet.
const cssFile = readdirSync(join(dist, 'assets')).find((f) => f.endsWith('.css'))
const css = cssFile ? readFileSync(join(dist, 'assets', cssFile), 'utf8') : ''
const missing = [...new Set(Object.values(C).join(' ').split(/\s+/))].filter((cls) => {
  const selector = `.${cls.replace(/[:/]/g, (m) => `\\${m}`)}`
  return !css.includes(selector)
})
if (missing.length) {
  console.warn(`prerender: classes not in the built CSS, will render unstyled: ${missing.join(', ')}`)
}

console.log(`prerender: ${routes.length} routes + 404.html written to dist/`)
