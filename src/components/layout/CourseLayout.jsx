import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Sidebar from './Sidebar.jsx'
import Footer from './Footer.jsx'

/** Track and module pages: navbar + persistent course tree + article. */
export default function CourseLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const { pathname } = useLocation()

  // Close the mobile drawer whenever the route changes, including via the
  // browser back button.
  useEffect(() => setDrawerOpen(false), [pathname])

  // Prevent the page behind the drawer from scrolling while it is open.
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [drawerOpen])

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar onMenuClick={() => setDrawerOpen(true)} />

      <div className="mx-auto flex w-full max-w-[110rem] flex-1 items-start">
        <Sidebar open={drawerOpen} onClose={() => setDrawerOpen(false)} />
        <div className="min-w-0 flex-1">
          <main>
            <Outlet />
          </main>
          <Footer />
        </div>
      </div>
    </div>
  )
}
