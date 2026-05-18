import { motion } from 'framer-motion';
import type { ConnectionState, PageId } from '../types';

const pageLabels: Array<{ id: PageId; label: string; short: string }> = [
  { id: 'training', label: 'CRUD', short: 'CRUD' },
  { id: 'council', label: 'Council', short: 'Council' },
  { id: 'labs', label: 'Kopano Labs', short: 'Labs' },
  { id: 'forge', label: 'Forge', short: 'Forge' },
  { id: 'console', label: 'Console', short: 'Console' },
];

interface AppTopNavProps {
  page: PageId;
  connectionState: ConnectionState;
  onNavigate: (page: PageId) => void;
}

export function AppTopNav({
  page,
  connectionState,
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
          <span>{connectionState === 'live' ? 'Local' : connectionState === 'connecting' ? 'Wake' : 'Check'}</span>
        </div>
        <div className="status-badge neutral">Owner-proof unproven</div>
      </div>
    </header>
  );
}
