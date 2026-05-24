import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initClientTelemetry } from './telemetry'
import { OperatorProvider } from './operator/OperatorProvider'

initClientTelemetry()

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <OperatorProvider>
      <App />
    </OperatorProvider>
  </React.StrictMode>,
)
