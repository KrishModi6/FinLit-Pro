import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Static SPA. `public/` is copied verbatim into `dist/` (robots.txt, sitemap.xml,
// og-image.png); everything else is bundled from `src/`.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
