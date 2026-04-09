import { motion } from 'framer-motion';
import type { LabsAnalytics, LabsOverview, MicrosoftReadiness, PageId } from '../types';

interface LabsPageProps {
  labsOverview: LabsOverview | null;
  labsAnalytics: LabsAnalytics | null;
  microsoftReadiness: MicrosoftReadiness | null;
  connectorResult: string;
  isAdminLoggedIn: boolean;
  onNavigate: (page: PageId) => void;
  onRunConnectorAction: (actionId: string) => void;
}

const interfaceDNA = [
  {
    title: 'Cursor + Codex clarity',
    copy: 'Fast action rails, code-grade structure, and direct controls that feel like tools instead of brochure cards.',
  },
  {
    title: 'Claude artifact calm',
    copy: 'Split surfaces, live previews, and enough breathing room for people to understand what is happening at a glance.',
  },
  {
    title: 'Perplexity trust cues',
    copy: 'Readable typography, proof-first summaries, and scannable evidence that makes the platform feel reliable under pressure.',
  },
];

export function LabsPage({
  labsOverview,
  labsAnalytics,
  microsoftReadiness,
  connectorResult,
  isAdminLoggedIn,
  onNavigate,
  onRunConnectorAction,
}: LabsPageProps) {
  const requiredRatio = microsoftReadiness
    ? `${microsoftReadiness.summary.required_ready}/${microsoftReadiness.summary.required_total}`
    : '0/6';

  return (
    <div className="page-layout labs-layout">
      <motion.section className="hero-panel hero-labs" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72 }}>
        <div className="hero-copy">
          <span className="eyebrow">Orch Labs</span>
          <div className="headline-stack">
            <span className="headline-line">Prompt less.</span>
            <span className="headline-line">Move faster.</span>
            <span className="headline-line">Show real proof.</span>
          </div>
          <p className="hero-copy-text">
            The public Labs surface now behaves like an AI studio: clean launch points, visible proof, and separate pages for the work people actually want to press.
          </p>
        </div>
        <div className="quick-launch-grid">
          <button type="button" className="quick-launch-card" onClick={() => onNavigate('forge')}>
            <span className="stat-label">Forge</span>
            <strong>{labsAnalytics?.forge.rooms ?? 0} live rooms</strong>
            <p>Turn demo ideas into tracked rooms, tasks, and artifacts.</p>
          </button>
          <button type="button" className="quick-launch-card" onClick={() => onNavigate('console')}>
            <span className="stat-label">Console</span>
            <strong>{labsAnalytics?.mcp_console.requests ?? 0} requests</strong>
            <p>Run guided MCP answers in a focused Claude-style split panel.</p>
          </button>
          <button type="button" className="quick-launch-card" onClick={() => onNavigate('admin')}>
            <span className="stat-label">Admin</span>
            <strong>{isAdminLoggedIn ? 'Unlocked' : 'Protected'}</strong>
            <p>Vault, activity preview, and internal controls stay clearly separated.</p>
          </button>
        </div>
      </motion.section>

      <section className="feature-grid three-up">
        {interfaceDNA.map((item, index) => (
          <motion.article
            key={item.title}
            className="glass-card trend-card"
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * index, duration: 0.58 }}
          >
            <span className="eyebrow">Interface DNA</span>
            <h2>{item.title}</h2>
            <p>{item.copy}</p>
          </motion.article>
        ))}
      </section>

      <div className="feature-grid">
        <motion.article className="glass-card readiness-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Microsoft path</span>
            <span className={`signal-chip ${microsoftReadiness?.summary.demo_ready ? 'live' : 'thinking'}`}>{requiredRatio}</span>
          </div>
          <h2>Live demo readiness</h2>
          <p>Cloud claims should feel earned. This card keeps the Microsoft story tied to real tooling, real auth, and real resource wiring.</p>
          {microsoftReadiness ? (
            <>
              <div className="readiness-grid">
                <article className="support-card">
                  <strong>CLI layer</strong>
                  <p>{microsoftReadiness.tooling.az.healthy && microsoftReadiness.tooling.azd.healthy ? 'az and azd are live in this shell.' : 'Fix the local toolchain before live claims.'}</p>
                </article>
                <article className="support-card">
                  <strong>Azure auth</strong>
                  <p>{microsoftReadiness.azure_account.logged_in ? microsoftReadiness.azure_account.subscription_name ?? 'Signed in' : 'Run az login.'}</p>
                </article>
                <article className="support-card">
                  <strong>Telemetry</strong>
                  <p>{microsoftReadiness.tooling.telemetry.configured ? 'Server is wired to App Insights.' : 'Connection string is still missing.'}</p>
                </article>
                <article className="support-card">
                  <strong>Azure OpenAI</strong>
                  <p>{microsoftReadiness.env.azure_openai.configured ? 'Endpoint, key, and deployment are present.' : microsoftReadiness.env.azure_openai.missing.join(', ')}</p>
                </article>
              </div>
              <div className="deliverable-stack">
                {microsoftReadiness.next_steps.map((step) => (
                  <div key={step} className="deliverable-pill">{step}</div>
                ))}
              </div>
            </>
          ) : (
            <p>Readiness is loading from the local Orch runtime.</p>
          )}
        </motion.article>

        <motion.article className="glass-card connector-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Actions</span>
            <span className="signal-chip neutral">{labsOverview?.installer_actions.length ?? 0} playbooks</span>
          </div>
          <h2>One-press playbooks</h2>
          <div className="action-list">
            {labsOverview?.installer_actions.slice(0, 4).map((action) => (
              <button key={action.id} type="button" className="playbook-button" onClick={() => onRunConnectorAction(action.id)}>
                <span>{action.title}</span>
                <small>{action.provider}</small>
              </button>
            ))}
          </div>
          <div className="console-output-panel">
            <pre>{connectorResult || 'Run a playbook to see the latest command path and readiness advice.'}</pre>
          </div>
        </motion.article>
      </div>

      <section className="feature-grid">
        <motion.article className="glass-card catalog-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Interfaces</span>
            <span className="signal-chip neutral">{labsOverview?.metrics.interfaces ?? 0} surfaces</span>
          </div>
          <h2>Public-facing surfaces</h2>
          <div className="catalog-grid">
            {labsOverview?.orch_interfaces.slice(0, 4).map((item) => (
              <article key={item.id} className="catalog-tile">
                <strong>{item.name}</strong>
                <p>{item.summary}</p>
              </article>
            ))}
          </div>
        </motion.article>

        <motion.article className="glass-card catalog-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Tool catalog</span>
            <span className="signal-chip neutral">{labsOverview?.metrics.live_tools ?? 0} live tools</span>
          </div>
          <h2>South African demo stack</h2>
          <div className="catalog-grid">
            {labsOverview?.tools.slice(0, 6).map((tool) => (
              <article key={tool.id} className="catalog-tile">
                <strong>{tool.name}</strong>
                <p>{tool.summary}</p>
              </article>
            ))}
          </div>
        </motion.article>
      </section>
    </div>
  );
}
