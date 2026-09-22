import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { getRouteMeta } from '../../data/seo.js'

/**
 * Keeps <head> in step with the route during client-side navigation.
 *
 * On a fresh load the static HTML written by scripts/prerender.mjs already
 * carries the right title, description and canonical for that URL. But
 * clicking a link swaps pages without a reload, and nothing else in the app
 * touches <head>, so without this the tab title, the canonical and the share
 * metadata would all stay frozen on whichever page the reader landed on.
 *
 * Reads from the same getRouteMeta the build uses, so the two cannot disagree.
 */

function setMeta(attribute, key, content) {
  let el = document.head.querySelector(`meta[${attribute}="${key}"]`)
  if (content == null) {
    el?.remove()
    return
  }
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attribute, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setCanonical(href) {
  let el = document.head.querySelector('link[rel="canonical"]')
  if (!href) {
    el?.remove()
    return
  }
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', 'canonical')
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

export default function RouteHead() {
  const { pathname } = useLocation()

  useEffect(() => {
    const meta = getRouteMeta(pathname)
    document.title = meta.title
    setMeta('name', 'description', meta.description)
    setMeta('name', 'robots', meta.robots)
    setCanonical(meta.canonical)
    setMeta('property', 'og:title', meta.title)
    setMeta('property', 'og:description', meta.description)
    setMeta('property', 'og:url', meta.url)
    setMeta('name', 'twitter:title', meta.title)
    setMeta('name', 'twitter:description', meta.description)
  }, [pathname])

  return null
}
