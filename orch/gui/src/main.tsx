import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import { initClientTelemetry } from './telemetry'

initClientTelemetry()

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
