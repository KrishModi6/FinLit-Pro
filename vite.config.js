import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Serves the `api/` serverless functions during `npm run dev`.
 *
 * In production Vercel runs these; the Vite dev server knows nothing about
 * them, so without this every /api call 404s locally and the market tools
 * cannot be tested without deploying. This mounts each handler behind the same
 * URL and shims the small bit of the Express-style response API they use.
 */
function apiDevServer() {
  return {
    name: 'api-dev-server',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        if (!req.url?.startsWith('/api/')) return next()

        const [pathname, search = ''] = req.url.split('?')
        const name = pathname.slice('/api/'.length).replace(/\.js$/, '')
        if (!/^[a-z0-9-]+$/i.test(name)) return next()

        try {
          const mod = await server.ssrLoadModule(`/api/${name}.js`)

          req.query = Object.fromEntries(new URLSearchParams(search))

          if (req.method === 'POST') {
            const chunks = []
            for await (const chunk of req) chunks.push(chunk)
            const raw = Buffer.concat(chunks).toString('utf8')
            try {
              req.body = raw ? JSON.parse(raw) : {}
            } catch {
              req.body = raw
            }
          }

          res.status = (code) => {
            res.statusCode = code
            return res
          }
          res.json = (payload) => {
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify(payload))
            return res
          }

          await mod.default(req, res)
        } catch (err) {
          server.config.logger.error(`[api-dev] ${name}: ${err?.stack ?? err}`)
          if (!res.headersSent) {
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
          }
          res.end(JSON.stringify({ error: `Local API error: ${err?.message ?? 'unknown'}` }))
        }
      })
    },
  }
}

// Static SPA plus serverless functions. `public/` is copied verbatim into
// `dist/` (robots.txt, sitemap.xml, og-image.png); everything else is bundled
// from `src/`, and `api/` is built by Vercel rather than Vite.
export default defineConfig({
  plugins: [react(), apiDevServer()],
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
