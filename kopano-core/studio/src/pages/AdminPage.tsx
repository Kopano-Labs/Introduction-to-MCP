import { AnimatePresence, motion } from 'framer-motion';
import type {
  FeedLogEntry,
  GuiUser,
  LabsAnalytics,
  Lesson,
  MicrosoftReadiness,
} from '../types';

interface AdminPageProps {
  isAdminLoggedIn: boolean;
  adminUser: GuiUser | null;
  adminEmail: string;
  adminPassword: string;
  adminError: string | null;
  adminLoading: boolean;
  sessions: Lesson[];
  selectedSession: Lesson | null;
  adminFeedPreview: FeedLogEntry[];
  labsAnalytics: LabsAnalytics | null;
  microsoftReadiness: MicrosoftReadiness | null;
  onAdminEmailChange: (value: string) => void;
  onAdminPasswordChange: (value: string) => void;
  onLogin: () => void;
  onLogout: () => void;
  onLoadSession: (id: string) => void;
  onOverrideScore: (blockId: string, score: number) => void;
}

export function AdminPage({
  isAdminLoggedIn,
  adminUser,
  adminEmail,
  adminPassword,
  adminError,
  adminLoading,
  sessions,
  selectedSession,
  adminFeedPreview,
  labsAnalytics,
  microsoftReadiness,
  onAdminEmailChange,
  onAdminPasswordChange,
  onLogin,
  onLogout,
  onLoadSession,
  onOverrideScore,
}: AdminPageProps) {
  return (
    <div className="page-layout admin-layout">
      <motion.section className="hero-panel hero-admin" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72 }}>
        <div className="hero-copy">
          <span className="eyebrow">Admin portal</span>
          <div className="headline-stack">
            <span className="headline-line">Internal only.</span>
            <span className="headline-line">Visible control.</span>
            <span className="headline-line">Real audit trails.</span>
          </div>
          <p className="hero-copy-text">
            Access deeper telemetry, session analytics, and forensic auditing traces behind the secure backend layer.
          </p>
        </div>
        <div className="quick-launch-grid compact">
          <article className="quick-launch-card static">
            <span className="stat-label">Access</span>
            <strong>{isAdminLoggedIn ? adminUser?.email : 'Locked'}</strong>
            <p>Only admin unlocks the vault and internal feed.</p>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Vault</span>
            <strong>{sessions.length}</strong>
            <p>Stored sessions available for forensic replay.</p>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Signals</span>
            <strong>{adminFeedPreview.length}</strong>
            <p>Recent runtime events visible to operators.</p>
          </article>
        </div>
      </motion.section>

      {!isAdminLoggedIn ? (
        <section className="feature-grid admin-login-grid">
          <motion.article className="glass-card composer-card" layout>
            <div className="card-topline">
              <span className="eyebrow">Authenticate</span>
              <span className="signal-chip alert">internal</span>
            </div>
            <h2>Open the admin portal</h2>
            <label className="field-shell">
              <span>Email</span>
              <input value={adminEmail} onChange={(event) => onAdminEmailChange(event.target.value)} />
            </label>
            <label className="field-shell">
              <span>Password</span>
              <input type="password" value={adminPassword} onChange={(event) => onAdminPasswordChange(event.target.value)} />
            </label>
            {adminError && <div className="admin-error">{adminError}</div>}
            <button type="button" className="action-button primary" onClick={onLogin}>
              {adminLoading ? 'Signing in...' : 'Open admin'}
            </button>
          </motion.article>

          <motion.article className="glass-card" layout>
            <div className="card-topline">
              <span className="eyebrow">Why it is split</span>
              <span className="signal-chip neutral">architecture</span>
            </div>
            <h2>What lives behind the wall</h2>
            <div className="deliverable-stack">
              <div className="deliverable-pill">Activity preview and operator relay</div>
              <div className="deliverable-pill">Session vault and forensic replay</div>
              <div className="deliverable-pill">Admin telemetry and cloud truth</div>
              <div className="deliverable-pill">Governance controls and optional score overrides</div>
            </div>
          </motion.article>
        </section>
      ) : (
        <>
          <section className="feature-grid">
            <motion.article className="glass-card journal-card" layout>
              <div className="card-topline">
                <span className="eyebrow">Activity preview</span>
                <span className="signal-chip live">{adminFeedPreview.length} live</span>
              </div>
              <h2>Operator relay</h2>
              <div className="timeline-list">
                {adminFeedPreview.map((entry) => (
                  <article key={entry.id} className="timeline-item">
                    <div className="timeline-meta">
                      <span>{entry.agent ? entry.agent.toUpperCase() : entry.type.toUpperCase()}</span>
                      <span>{new Date(entry.received_at).toLocaleTimeString()}</span>
                    </div>
                    <p>{entry.content ?? entry.reasoning ?? 'Runtime event captured.'}</p>
                  </article>
                ))}
              </div>
            </motion.article>

            <motion.article className="glass-card" layout>
              <div className="card-topline">
                <span className="eyebrow">Ops snapshot</span>
                <span className="signal-chip neutral">internal</span>
              </div>
              <h2>Runtime posture</h2>
              <div className="readiness-grid">
                <article className="support-card">
                  <strong>Console requests</strong>
                  <p>{labsAnalytics?.mcp_console.requests ?? 0}</p>
                </article>
                <article className="support-card">
                  <strong>Forge tasks</strong>
                  <p>{labsAnalytics?.forge.tasks ?? 0}</p>
                </article>
                <article className="support-card">
                  <strong>Microsoft required</strong>
                  <p>{microsoftReadiness ? `${microsoftReadiness.summary.required_ready}/${microsoftReadiness.summary.required_total}` : 'loading'}</p>
                </article>
                <article className="support-card">
                  <strong>Admin mode</strong>
                  <p>{adminUser?.email}</p>
                </article>
              </div>
              <button type="button" className="action-button ghost" onClick={onLogout}>Log out</button>
            </motion.article>
          </section>

          <section className="feature-grid admin-detail-grid">
            <motion.article className="glass-card vault-card" layout>
              <div className="card-topline">
                <span className="eyebrow">Session vault</span>
                <span className="signal-chip neutral">{sessions.length}</span>
              </div>
              <h2>Forensic sessions</h2>
              <div className="vault-list">
                {sessions.map((session) => (
                  <button key={session.id} type="button" className={`vault-item ${selectedSession?.id === session.id ? 'active' : ''}`} onClick={() => onLoadSession(session.id)}>
                    <span>{session.topic}</span>
                    <small>{session.round_count ?? 0} rounds · {session.audit_events ?? 0} audit events</small>
                  </button>
                ))}
              </div>
            </motion.article>

            <motion.article className="glass-card audit-panel" layout>
              <div className="card-topline">
                <span className="eyebrow">Audit</span>
                <span className="signal-chip neutral">{selectedSession?.topic ?? 'select a session'}</span>
              </div>
              <AnimatePresence mode="wait">
                {selectedSession ? (
                  <motion.div key={selectedSession.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                    <h2>{selectedSession.topic}</h2>
                    {selectedSession.rounds?.length ? (
                      <div className="audit-round-list">
                        {selectedSession.rounds.map((round) => (
                          <section key={round.id} className="audit-round">
                            <div className="timeline-meta">
                              <span>Round {round.round_number}</span>
                              <span>{round.blocks.length} blocks</span>
                            </div>
                            <div className="audit-block-list">
                              {round.blocks.map((block) => (
                                <article key={block.block_id} className="audit-block-card">
                                  <div className="lane-task-top">
                                    <strong>{block.agent.toUpperCase()}</strong>
                                    <span className="signal-chip neutral">{block.override_score ?? block.value_score}/10</span>
                                  </div>
                                  <p>{block.content}</p>
                                  <small>{block.reasoning}</small>
                                  <label className="field-shell compact">
                                    <span>Override</span>
                                    <input
                                      type="range"
                                      min="0"
                                      max="10"
                                      value={block.override_score ?? block.value_score ?? 0}
                                      onChange={(event) => onOverrideScore(block.block_id, Number.parseInt(event.target.value, 10))}
                                    />
                                  </label>
                                </article>
                              ))}
                            </div>
                          </section>
                        ))}
                      </div>
                    ) : (
                      <div className="timeline-item empty">
                        <div className="timeline-meta">
                          <span>Vault</span>
                          <span>waiting</span>
                        </div>
                        <p>This session has no recorded forensic rounds. Select an active session to view its auditable reasoning traces.</p>
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <motion.div key="empty" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                    <h2>Select a session</h2>
                    <p>Choose a session from the vault to open its rounds, reasoning blocks, and optional score override controls.</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.article>
          </section>
        </>
      )}
    </div>
  );
}
