import { Route, Routes } from 'react-router-dom'
import ScrollToTop from './components/layout/ScrollToTop.jsx'
import SiteLayout from './components/layout/SiteLayout.jsx'
import CourseLayout from './components/layout/CourseLayout.jsx'
import SimulatorLayout from './pages/simulator/SimulatorLayout.jsx'
import SimulatorHome from './pages/simulator/SimulatorHome.jsx'
import SimulatorTool from './pages/simulator/index.jsx'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Glossary from './pages/Glossary.jsx'
import TrackPage from './pages/TrackPage.jsx'
import ModulePage from './pages/ModulePage.jsx'
import NotFound from './pages/NotFound.jsx'

/**
 * Routing.
 *
 * React Router v6 ranks static segments above dynamic ones, so `/glossary` and
 * `/simulator` resolve to their own pages rather than being swallowed by
 * `/:trackSlug`. An unknown `:trackSlug` falls through to the 404 rendered
 * inside TrackPage.
 */
export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<SiteLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/glossary" element={<Glossary />} />
          <Route path="*" element={<NotFound />} />
        </Route>

        {/* The simulator sits alongside the course, with its own chrome. */}
        <Route element={<SimulatorLayout />}>
          <Route path="/simulator" element={<SimulatorHome />} />
          <Route path="/simulator/:toolSlug" element={<SimulatorTool />} />
        </Route>

        <Route element={<CourseLayout />}>
          <Route path="/:trackSlug" element={<TrackPage />} />
          <Route path="/:trackSlug/:moduleSlug" element={<ModulePage />} />
        </Route>
      </Routes>
    </>
  )
}
