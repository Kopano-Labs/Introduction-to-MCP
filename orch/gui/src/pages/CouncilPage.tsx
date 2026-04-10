import { motion } from 'framer-motion';
import type { ConnectionState, CouncilCard, FeedLogEntry, LiveMessage, PageId } from '../types';

interface CouncilPageProps {
  connectionState: ConnectionState;
  featuredCard: CouncilCard;
  supportCards: CouncilCard[];
  latestTransmission: LiveMessage | null;
  feedPreview: FeedLogEntry[];
  sessionCount: number;
  onNavigate: (page: PageId) => void;
}

const heroLines = ['Fast local AI,', 'framed for live', 'decisions.'];

export function CouncilPage({
  connectionState,
  featuredCard,
  supportCards,
  latestTransmission,
  feedPreview,
  sessionCount,
  onNavigate,
}: CouncilPageProps) {
  const liveStateLabel = connectionState === 'live' ? 'Council is live' : connectionState === 'connecting' ? 'Linking the room' : 'Signal needs attention';
  const liveCopy = latestTransmission?.content
    ?? 'Quiet moments should still feel intentional. The council keeps the stage warm with visible state, a listening orb, and a living relay of what just happened.';

  return (
    <div className="page-layout council-layout">
      <motion.section
        className="hero-panel hero-council"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="hero-copy">
          <span className="eyebrow">Live Council</span>
          <div className="headline-stack">
            {heroLines.map((line, index) => (
              <motion.span
                key={line}
                className="headline-line"
                initial={{ opacity: 0, y: 44 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 * index, duration: 0.72, ease: [0.16, 1, 0.3, 1] }}
              >
                {line}
              </motion.span>
            ))}
          </div>
          <p className="hero-copy-text">{liveCopy}</p>
          <div className="hero-actions">
            <button type="button" className="action-button primary" onClick={() => onNavigate('labs')}>Open Labs</button>
            <button type="button" className="action-button secondary" onClick={() => onNavigate('console')}>Open Console</button>
          </div>
          <div className="hero-stat-row">
            <article className="glass-stat">
              <span className="stat-label">Link</span>
              <strong>{liveStateLabel}</strong>
            </article>
            <article className="glass-stat">
              <span className="stat-label">Signals</span>
              <strong>{feedPreview.length}</strong>
            </article>
            <article className="glass-stat">
              <span className="stat-label">Vault</span>
              <strong>{sessionCount} sessions</strong>
            </article>
          </div>
        </div>

        <motion.div
          className="hero-orb-shell"
          animate={{ y: [0, -10, 0], rotate: [0, 3, 0] }}
          transition={{ duration: 7.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <motion.div
            className={`hero-orb ${connectionState}`}
            animate={{ scale: [1, 1.08, 1], opacity: [0.74, 1, 0.78] }}
            transition={{ duration: 3.4, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="hero-orb-ring"
            animate={{ scale: [0.92, 1.18], opacity: [0.44, 0] }}
            transition={{ duration: 2.6, repeat: Infinity, ease: 'easeOut' }}
          />
          <div className="orb-caption">
            <span>{featuredCard.id.toUpperCase()}</span>
            <strong>{featuredCard.isResponding ? 'Speaking now' : featuredCard.isThinking ? 'Reasoning' : 'Standing by'}</strong>
          </div>
        </motion.div>
      </motion.section>

      <div className="feature-grid">
        <motion.article className="glass-card spotlight-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Featured voice</span>
            <span className={`signal-chip ${featuredCard.isResponding ? 'live' : featuredCard.isThinking ? 'thinking' : 'idle'}`}>
              {featuredCard.isResponding ? 'Responding' : featuredCard.isThinking ? 'Thinking' : 'Idle'}
            </span>
          </div>
          <h2>{featuredCard.id.toUpperCase()}</h2>
          <p className="card-lead">{featuredCard.lastMsg?.content ?? 'No live signal yet. Seed one `/broadcast` event before presenting so the council opens with visible proof instead of waiting.'}</p>
          <div className="reasoning-rail">
            <span className="reasoning-label">Reasoning trace</span>
            <p>{featuredCard.lastMsg?.reasoning ?? 'Support voices remain visible so the room still feels alive while waiting for the next trigger.'}</p>
          </div>
        </motion.article>

        <motion.article className="glass-card support-card-shell" layout>
          <div className="card-topline">
            <span className="eyebrow">Bench voices</span>
            <span className="signal-chip neutral">{supportCards.length} active lanes</span>
          </div>
          <div className="support-card-grid">
            {supportCards.map((card, index) => (
              <motion.article
                key={card.id}
                className="support-card"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.06 * index }}
              >
                <div className="support-card-top">
                  <strong>{card.id.toUpperCase()}</strong>
                  <span className={`signal-chip ${card.isResponding ? 'live' : card.isThinking ? 'thinking' : 'idle'}`}>
                    {card.isResponding ? 'Live' : card.isThinking ? 'Thinking' : 'Idle'}
                  </span>
                </div>
                <p>{card.lastMsg?.content ?? 'Awaiting the next handoff.'}</p>
              </motion.article>
            ))}
          </div>
        </motion.article>
      </div>

      <motion.section className="glass-card journal-card" layout>
        <div className="card-topline">
          <span className="eyebrow">Live relay</span>
          <span className="signal-chip neutral">{feedPreview.length} updates</span>
        </div>
        <div className="timeline-list">
          {feedPreview.length > 0 ? (
            feedPreview.map((entry) => (
              <motion.article key={entry.id} className="timeline-item" layout>
                <div className="timeline-meta">
                  <span>{entry.agent ? entry.agent.toUpperCase() : entry.type.toUpperCase()}</span>
                  <span>{new Date(entry.received_at).toLocaleTimeString()}</span>
                </div>
                <p>{entry.content ?? entry.reasoning ?? 'Council event captured.'}</p>
              </motion.article>
            ))
          ) : (
            <article className="timeline-item empty">
              <div className="timeline-meta">
                <span>System</span>
                <span>waiting</span>
              </div>
              <p>The relay is ready. The next websocket or polled event will appear here with motion instead of dead air.</p>
            </article>
          )}
        </div>
      </motion.section>
    </div>
  );
}
