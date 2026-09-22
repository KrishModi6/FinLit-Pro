/**
 * Generates public/sitemap.xml from src/data/seo.js, the same list of
 * indexable routes the prerender step writes files for, so the sitemap can
 * never name a page that does not exist or omit one that does. Runs as part
 * of `npm run build`.
 *
 * Only <loc> is emitted, deliberately. Google ignores <changefreq> and
 * <priority> outright, and uses <lastmod> only when it is consistently
 * accurate. The old sitemap stamped every URL with the build date, which
 * claimed all 46 pages changed on every deploy; that is the pattern Google
 * learns to disregard. No date is better than a wrong one.
 *
 * /dashboard is absent because seo.js marks it noindex: it renders one
 * browser's LocalStorage and has nothing for a crawler.
 */
import { writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { absoluteUrl, listIndexableRoutes } from '../src/data/seo.js'

const here = dirname(fileURLToPath(import.meta.url))
const routes = listIndexableRoutes()

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${routes.map((r) => `  <url><loc>${absoluteUrl(r)}</loc></url>`).join('\n')}
</urlset>
`

writeFileSync(resolve(here, '../public/sitemap.xml'), xml, 'utf8')
console.log(`sitemap: ${routes.length} URLs → public/sitemap.xml`)
