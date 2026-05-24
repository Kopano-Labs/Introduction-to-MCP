import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';

type BootState = 'starting' | 'ready' | 'timeout';

export function DesktopBootOverlay() {
  const [state, setState] = useState<BootState>('starting');

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const maxAttempts = 240;

    const poll = async () => {
      while (!cancelled && attempts < maxAttempts) {
        attempts += 1;
        try {
          const response = await fetch(`${getApiBase()}/health`);
          if (response.ok) {
            setState('ready');
            return;
          }
        } catch {
          // Server still warming up.
        }
        await new Promise((resolve) => window.setTimeout(resolve, 500));
      }
      if (!cancelled) {
        setState('timeout');
      }
    };

    void poll();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state === 'ready') {
    return null;
  }

  return (
    <motion.div className="desktop-boot-overlay" role="status" aria-live="polite">
      <div className="desktop-boot-card">
        <span className="eyebrow">Kopano Context</span>
        <h2>{state === 'timeout' ? 'Still starting…' : 'Starting local runtime'}</h2>
        <p>
          {state === 'timeout'
            ? 'The API is taking longer than usual. You can keep waiting or reload once the server is up.'
            : 'Loading Studio, vault, and admin services. First launch can take up to a minute.'}
        </p>
        <motion.span
          className="desktop-boot-spinner"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.1, ease: 'linear' }}
        />
      </div>
    </motion.div>
  );
}
