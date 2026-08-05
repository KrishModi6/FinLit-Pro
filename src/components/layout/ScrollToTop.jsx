import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/**
 * React Router preserves scroll position across navigations, which is wrong for
 * a course: clicking the next lesson should start you at the top of it, not
 * halfway down. Anchor links (#quiz) are left alone.
 */
export default function ScrollToTop() {
  const { pathname, hash } = useLocation()

  useEffect(() => {
    if (hash) return
    // Jump, don't animate, the smooth-scroll in index.css is for anchors.
    window.scrollTo(0, 0)
  }, [pathname, hash])

  return null
}
