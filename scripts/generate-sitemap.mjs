/**
 * Generates public/sitemap.xml from the curriculum, so the sitemap can never
 * drift out of sync with the actual routes. Runs as part of `npm run build`.
 *
 * `src/data/curriculum.js` deliberately has no imports of its own, which is what
 * lets plain Node load it without a bundler or JSX transform.
 */
import { writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { TRACKS } from '../src/data/curriculum.js'

const ORIGIN = 'https://www.finlitpro.org'
const here = dirname(fileURLToPath(import.meta.url))
const today = new Date().toISOString().slice(0, 10)

const routes = [
  { loc: '/', priority: '1.0', changefreq: 'weekly' },
  { loc: '/glossary', priority: '0.7', changefreq: 'monthly' },
  ...TRACKS.flatMap((track) => [
    { loc: track.path, priority: '0.9', changefreq: 'monthly' },
    ...track.modules.map((mod) => ({ loc: mod.path, priority: '0.8', changefreq: 'monthly' })),
  ]),
]

// /dashboard is intentionally absent: it renders per-browser LocalStorage state
// and has nothing useful for a crawler to index.

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${routes
  .map(
    (r) => `  <url>
    <loc>${ORIGIN}${r.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${r.changefreq}</changefreq>
    <priority>${r.priority}</priority>
  </url>`
  )
  .join('\n')}
</urlset>
`

const out = resolve(here, '../public/sitemap.xml')
writeFileSync(out, xml, 'utf8')
console.log(`sitemap: ${routes.length} URLs → public/sitemap.xml`)
