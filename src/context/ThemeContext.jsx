import { createContext, useCallback, useContext, useEffect, useState } from 'react'

const STORAGE_KEY = 'stockguide:theme'

const ThemeContext = createContext(null)

/**
 * Light/dark theme, persisted to LocalStorage.
 *
 * The *initial* value is read from the class that the inline script in
 * index.html already put on <html>, that script runs before first paint so
 * dark-mode users never get a white flash. This provider just keeps React and
 * the DOM in sync from then on.
 */
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    if (typeof document === 'undefined') return 'light'
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light'
  })

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    try {
      localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // Private browsing / storage disabled, the theme still works this session.
    }
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }, [])

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>')
  return ctx
}
