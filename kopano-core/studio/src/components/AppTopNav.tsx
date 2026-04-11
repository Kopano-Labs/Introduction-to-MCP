import { motion } from 'framer-motion';
import type { ConnectionState, PageId } from '../types';

const pageLabels: Array<{ id: PageId; label: string; short: string }> = [
  { id: 'council', label: 'Live Council', short: 'Council' },
  { id: 'labs', label: 'Kopano Labs', short: 'Labs' },
  { id: 'forge', label: 'Forge', short: 'Forge' },
  { id: 'console', label: 'Console', short: 'Console' },
  { id: 'admin', label: 'Admin', short: 'Admin' },
];

interface AppTopNavProps {
  page: PageId;
  connectionState: ConnectionState;
  sessionCount: number;
  isAdminLoggedIn: boolean;
  onNavigate: (page: PageId) => void;
}

export function AppTopNav({
  page,
  connectionState,
  sessionCount,
  isAdminLoggedIn,
  onNavigate,
}: AppTopNavProps) {
  return (
    <header className="app-topbar">
      <motion.button
        type="button"
        className="brand-lockup"
        onClick={() => onNavigate('council')}
        whileHover={{ y: -2, scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <span className="brand-mark">
          <span>OR</span>
        </span>
        <span className="brand-copy">
          <strong>Kopano</strong>
          <span>South African AI operating shell</span>
        </span>
      </motion.button>

      <nav className="primary-nav" aria-label="Primary">
        {pageLabels.map((item) => {
          const isActive = item.id === page;
          return (
            <motion.button
              key={item.id}
              type="button"
              className={`nav-pill ${isActive ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              {isActive && <motion.span className="nav-pill-glow" layoutId="nav-pill-glow" transition={{ type: 'spring', stiffness: 280, damping: 28 }} />}
              <span>{item.label}</span>
            </motion.button>
          );
        })}
      </nav>

      <div className="topbar-badges">
        <div className={`status-badge ${connectionState}`}>
          <span className="status-dot" />
          <span>{connectionState === 'live' ? 'Live link' : connectionState === 'connecting' ? 'Connecting' : 'Attention'}</span>
        </div>
        <div className="status-badge neutral">{sessionCount} sessions</div>
        <div className={`status-badge ${isAdminLoggedIn ? 'live' : 'neutral'}`}>
          {isAdminLoggedIn ? 'Admin mode' : 'Public mode'}
        </div>
      </div>
    </header>
  );
}
