import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { ProgressProvider } from './context/ProgressContext.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <ProgressProvider>
          <App />
        </ProgressProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
