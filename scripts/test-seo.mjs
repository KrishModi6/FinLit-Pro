/**
 * Tests for per-route search metadata (src/data/seo.js).  Run with `npm test`.
 *
 * The properties here are the ones search engines actually punish when they
 * break: two pages with one title, a page naming someone else as its
 * canonical, a private page asking to be indexed. Each was true of every page
 * on the site before seo.js existed.
 */
import {
  DESCRIPTION_MAX,
  TITLE_MAX,
  SITE_ORIGIN,
  getRouteMeta,
  listIndexableRoutes,
  listPrerenderRoutes,
  normalisePath,
} from '../src/data/seo.js'

let pass = 0
let fail = 0
const check = (label, ok, detail = '') => {
  ok ? pass++ : fail++
  console.log(`  ${ok ? 'ok  ' : 'FAIL'}  ${label}${!ok && detail ? `\n        ${detail}` : ''}`)
}
const dupes = (values) => values.filter((v, i) => values.indexOf(v) !== i)

const routes = listIndexableRoutes()
const metas = routes.map((r) => getRouteMeta(r))

console.log(`\nindexable routes: ${routes.length}`)
check('no route is listed twice', dupes(routes).length === 0, dupes(routes).join(', '))

console.log('\nevery indexable page names itself as canonical')
const wrongCanonical = metas.filter((m) => m.canonical !== `${SITE_ORIGIN}${m.path}`)
check('canonical is self-referential on all of them', wrongCanonical.length === 0,
  wrongCanonical.map((m) => `${m.path} -> ${m.canonical}`).join('\n        '))
check('none of them points at the homepage except the homepage',
  metas.every((m) => m.path === '/' || m.canonical !== `${SITE_ORIGIN}/`))
check('all are indexable', metas.every((m) => m.indexable && /^index/.test(m.robots)))

console.log('\nevery indexable page is distinguishable')
const titles = metas.map((m) => m.title)
const descs = metas.map((m) => m.description)
check('titles are unique', dupes(titles).length === 0, dupes(titles).join(' | '))
check('descriptions are unique', dupes(descs).length === 0, dupes(descs).join(' | '))
check('h1s are unique', dupes(metas.map((m) => m.h1)).length === 0, dupes(metas.map((m) => m.h1)).join(' | '))

console.log('\nlengths search results can actually show')
const longDesc = metas.filter((m) => m.description.length > DESCRIPTION_MAX)
check(`descriptions are at most ${DESCRIPTION_MAX} characters`, longDesc.length === 0,
  longDesc.map((m) => `${m.path} (${m.description.length})`).join(', '))
const longTitle = metas.filter((m) => m.title.length > TITLE_MAX)
check(`titles are at most ${TITLE_MAX} characters`, longTitle.length === 0,
  longTitle.map((m) => `${m.path} (${m.title.length})`).join(', '))
check('no description is truncated with an ellipsis', metas.every((m) => !m.description.endsWith('…')),
  metas.filter((m) => m.description.endsWith('…')).map((m) => m.path).join(', '))
const shortDesc = metas.filter((m) => m.description.length < 50)
check('descriptions are at least 50 characters', shortDesc.length === 0,
  shortDesc.map((m) => `${m.path} (${m.description.length})`).join(', '))
check('no description is cut mid-word', metas.every((m) => !/\w…$/.test(m.description) || / \S+…$/.test(m.description)))
check('no em dashes in any title or description', metas.every((m) => !/—/.test(m.title + m.description)))

console.log('\npages that must stay out of search')
const dash = getRouteMeta('/dashboard')
check('/dashboard is noindex', dash.robots.startsWith('noindex'))
check('/dashboard has no canonical', dash.canonical === null)
check('/dashboard is prerendered but not in the sitemap list',
  listPrerenderRoutes().includes('/dashboard') && !routes.includes('/dashboard'))
for (const bad of ['/nope', '/beginner/not-a-lesson', '/simulator/not-a-tool', '/a/b/c']) {
  const m = getRouteMeta(bad)
  check(`${bad} resolves to a noindex not-found page`, m.robots.startsWith('noindex') && /Not Found/.test(m.title))
}

console.log('\npath normalisation matches what a browser can send')
check('trailing slash', normalisePath('/beginner/') === '/beginner')
check('query string', normalisePath('/simulator/market?symbol=AAPL') === '/simulator/market')
check('hash', normalisePath('/glossary#beta') === '/glossary')
check('root stays root', normalisePath('/') === '/' && normalisePath('') === '/')
check('trailing slash resolves to the same page',
  getRouteMeta('/beginner/what-is-a-stock/').title === getRouteMeta('/beginner/what-is-a-stock').title)

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
