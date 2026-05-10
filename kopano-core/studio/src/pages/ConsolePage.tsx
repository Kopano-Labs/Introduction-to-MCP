import { motion } from 'framer-motion';
import type { FeedLogEntry, LabsAnalytics, McpConsoleReply } from '../types';

interface ConsolePageProps {
  consoleMessage: string;
  consoleReply: McpConsoleReply | null;
  consoleStream: string;
  selectedModel: string;
  feedPreview: FeedLogEntry[];
  labsAnalytics: LabsAnalytics | null;
  onConsoleMessageChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onSend: () => void;
  onStream: () => void;
}

export function ConsolePage({
  consoleMessage,
  consoleReply,
  consoleStream,
  selectedModel,
  feedPreview,
  labsAnalytics,
  onConsoleMessageChange,
  onModelChange,
  onSend,
  onStream,
}: ConsolePageProps) {
  const modelOptions = consoleReply?.model_options ?? [{ id: 'deterministic', label: 'deterministic fallback', model: 'deterministic-fallback' }];

  return (
    <div className="page-layout console-layout">
      <motion.section className="hero-panel ops-hero hero-console" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72 }}>
        <div className="ops-title">
          <span className="eyebrow">Console</span>
          <h2>Runtime request</h2>
          <p>Send a request and inspect the returned artifact.</p>
        </div>
        <div className="ops-stat-grid">
          <article className="quick-launch-card static">
            <span className="stat-label">Requests</span>
            <strong>{labsAnalytics?.mcp_console.requests ?? 0}</strong>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Sessions</span>
            <strong>{labsAnalytics?.mcp_console.sessions ?? 0}</strong>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Latency</span>
            <strong>{labsAnalytics?.mcp_console.average_latency_ms ?? 0}ms</strong>
          </article>
        </div>
      </motion.section>

      <section className="feature-grid console-split">
        <motion.article className="glass-card console-composer" layout>
          <div className="card-topline">
            <span className="eyebrow">Compose</span>
            <span className="signal-chip live">MCP</span>
          </div>
          <h2>Request</h2>
          <label className="field-shell">
            <span>Model</span>
            <select value={selectedModel} onChange={(event) => onModelChange(event.target.value)}>
              {modelOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
          <label className="field-shell">
            <span>Prompt</span>
            <textarea rows={6} value={consoleMessage} onChange={(event) => onConsoleMessageChange(event.target.value)} />
          </label>
          <div className="button-row">
            <button type="button" className="action-button primary" onClick={onSend}>Send</button>
            <button type="button" className="action-button ghost" onClick={onStream}>Stream</button>
          </div>
        </motion.article>

        <motion.article className="glass-card console-output" layout>
          <div className="card-topline">
            <span className="eyebrow">Artifact</span>
            <span className="signal-chip neutral">{consoleReply?.topic ?? 'waiting'}</span>
          </div>
          <h2>{consoleReply?.model_used ?? 'No response'}</h2>
          <div className="console-output-panel tall">
            <p>{consoleStream || consoleReply?.response || 'Send a message to show grounded guidance, suggested actions, and surface routing.'}</p>
          </div>
          {consoleReply && (
            <>
              <div className="pill-stack">
                {consoleReply.suggested_actions.map((action) => <div key={action} className="deliverable-pill">{action}</div>)}
              </div>
              <div className="badge-cluster">
                {consoleReply.surfaces.map((surface) => <span key={surface} className="status-badge neutral">{surface}</span>)}
              </div>
            </>
          )}
        </motion.article>
      </section>

      <motion.section className="glass-card relay-card" layout>
        <div className="card-topline">
          <span className="eyebrow">Live relay</span>
          <span className="signal-chip neutral">{feedPreview.length} council signals</span>
        </div>
        <div className="timeline-list">
          {feedPreview.length > 0 ? (
            feedPreview.map((entry) => (
              <article key={entry.id} className="timeline-item">
                <div className="timeline-meta">
                  <span>{entry.agent ? entry.agent.toUpperCase() : entry.type.toUpperCase()}</span>
                  <span>{new Date(entry.received_at).toLocaleTimeString()}</span>
                </div>
                <p>{entry.content ?? entry.reasoning ?? 'Live council event captured.'}</p>
              </article>
            ))
          ) : (
            <article className="timeline-item empty">
              <div className="timeline-meta">
                <span>Relay</span>
                <span>idle</span>
              </div>
              <p>The event relay is connected. Awaiting backend propagation or explicit CLI commands.</p>
            </article>
          )}
        </div>
      </motion.section>
    </div>
  );
}
