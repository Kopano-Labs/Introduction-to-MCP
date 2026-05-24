import { motion } from 'framer-motion';
import type { ConnectionState, PageId } from '../types';

const pageLabels: Array<{ id: PageId; label: string; short: string }> = [
  { id: 'training', label: 'CRUD', short: 'CRUD' },
  { id: 'council', label: 'Council', short: 'Council' },
  { id: 'labs', label: 'Kopano Labs', short: 'Labs' },
  { id: 'forge', label: 'Forge', short: 'Forge' },
  { id: 'console', label: 'Swarm Console', short: 'Swarm' },
  { id: 'admin', label: 'Admin', short: 'Admin' },
];

interface AppTopNavProps {
  page: PageId;
  connectionState: ConnectionState;
  isAdminLoggedIn: boolean;
  isGodMode: boolean;
  onNavigate: (page: PageId) => void;
}

export function AppTopNav({
  page,
  connectionState,
  isAdminLoggedIn,
  isGodMode,
  onNavigate,
}: AppTopNavProps) {
  return (
    <header className="app-topbar">
      <motion.button
        type="button"
        className="brand-lockup"
        onClick={() => onNavigate('training')}
        whileHover={{ y: -2, scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <span className="brand-mark">
          <span>KC</span>
        </span>
        <span className="brand-copy">
          <strong>Kopano Context</strong>
          <span>Cassey · Council · Console</span>
        </span>
      </motion.button>

      <nav className="primary-nav" aria-label="Primary">
        {pageLabels.map((item) => {
          const isActive = item.id === page;
          const isAdmin = item.id === 'admin';
          return (
            <motion.button
              key={item.id}
              type="button"
              className={`nav-pill ${isActive ? 'active' : ''} ${isAdmin ? 'nav-pill-admin' : ''}`}
              onClick={() => onNavigate(item.id)}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              {isActive && <motion.span className="nav-pill-glow" layoutId="nav-pill-glow" transition={{ type: 'spring', stiffness: 280, damping: 28 }} />}
              <span>{item.label}</span>
              {isAdmin && !isAdminLoggedIn && <span className="nav-lock-dot" aria-label="Admin locked" />}
            </motion.button>
          );
        })}
      </nav>

      <div className="topbar-badges">
        <div className={`status-badge ${connectionState}`}>
          <span className="status-dot" />
          <span>{connectionState === 'live' ? 'Local' : connectionState === 'connecting' ? 'Wake' : 'Check'}</span>
        </div>
        <div className={`status-badge ${isGodMode ? 'live' : 'neutral'}`}>
          {isGodMode ? 'Super God · Cassy' : 'God locked'}
        </div>
        <div className={`status-badge ${isAdminLoggedIn ? 'live' : 'neutral'}`}>
          {isAdminLoggedIn ? 'Admin session' : 'Admin locked'}
        </div>
      </div>
    </header>
  );
}
