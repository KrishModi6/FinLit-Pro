import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Footer from './Footer.jsx'

/** Full-width pages: home, dashboard, glossary, 404. No lesson sidebar. */
export default function SiteLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
