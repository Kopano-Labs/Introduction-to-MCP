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
      <motion.section className="hero-panel ops-hero hero-labs" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72 }}>
        <div className="ops-title">
          <span className="eyebrow">Kopano Labs</span>
          <h2>Runtime surfaces</h2>
          <p>Open tools, readiness checks, and local playbooks.</p>
        </div>
        <div className="ops-stat-grid">
          <button type="button" className="quick-launch-card" onClick={() => onNavigate('console')}>
            <span className="stat-label">Console</span>
            <strong>{labsAnalytics?.mcp_console.requests ?? 0} requests</strong>
          </button>
          <button type="button" className="quick-launch-card" onClick={() => onNavigate('forge')}>
            <span className="stat-label">Forge</span>
            <strong>{labsAnalytics?.forge.rooms ?? 0} live rooms</strong>
          </button>
          <article className="quick-launch-card static">
            <span className="stat-label">Readiness</span>
            <strong>{requiredRatio}</strong>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Audit</span>
            <strong>{isAdminLoggedIn ? 'Unlocked' : 'Locked'}</strong>
          </article>
        </div>
      </motion.section>

      <div className="feature-grid">
        <motion.article className="glass-card readiness-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Microsoft path</span>
            <span className={`signal-chip ${microsoftReadiness?.summary.demo_ready ? 'live' : 'thinking'}`}>{requiredRatio}</span>
          </div>
          <h2>Readiness</h2>
          {microsoftReadiness ? (
            <>
              <div className="readiness-grid">
                <article className="support-card">
                  <strong>CLI layer</strong>
                  <p>{microsoftReadiness.tooling.az.healthy && microsoftReadiness.tooling.azd.healthy ? 'az and azd are ready in this shell for buyer-facing rehearsal.' : 'Fix the local toolchain before making any Azure claim.'}</p>
                </article>
                <article className="support-card">
                  <strong>Azure auth</strong>
                  <p>{microsoftReadiness.azure_account.logged_in ? microsoftReadiness.azure_account.subscription_name ?? 'Signed in' : 'Owner must run az login before any live Azure claim.'}</p>
                </article>
                <article className="support-card">
                  <strong>Telemetry</strong>
                  <p>{microsoftReadiness.tooling.telemetry.configured ? 'Server is wired to App Insights.' : 'App Insights hooks exist, but real connection strings are still missing.'}</p>
                </article>
                <article className="support-card">
                  <strong>Azure OpenAI</strong>
                  <p>{microsoftReadiness.env.azure_openai.configured ? 'Endpoint, key, and deployment are present.' : `Owner must supply ${microsoftReadiness.env.azure_openai.missing.join(', ')}.`}</p>
                </article>
              </div>
              <div className="deliverable-stack">
                {microsoftReadiness.next_steps.map((step) => (
                  <div key={step} className="deliverable-pill">{step}</div>
                ))}
              </div>
            </>
          ) : (
            <p>Readiness is loading from the local Kopano runtime so the Microsoft claim stays tied to evidence.</p>
          )}
        </motion.article>

        <motion.article className="glass-card connector-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Actions</span>
            <span className="signal-chip neutral">{labsOverview?.installer_actions.length ?? 0} playbooks</span>
          </div>
          <h2>Playbooks</h2>
          <div className="action-list">
            {labsOverview?.installer_actions.slice(0, 4).map((action) => (
              <button key={action.id} type="button" className="playbook-button" onClick={() => onRunConnectorAction(action.id)}>
                <span>{action.title}</span>
                <small>{action.provider}</small>
              </button>
            ))}
          </div>
          <div className="console-output-panel">
            <pre>{connectorResult || 'Run a playbook to show the latest command path, fallback wording, and readiness advice.'}</pre>
          </div>
        </motion.article>
      </div>

      <section className="feature-grid">
        <motion.article className="glass-card catalog-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Interfaces</span>
            <span className="signal-chip neutral">{labsOverview?.metrics.interfaces ?? 0} surfaces</span>
          </div>
          <h2>Surfaces</h2>
          <div className="catalog-grid">
            {labsOverview?.kopano_interfaces.slice(0, 4).map((item) => (
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
          <h2>Tools</h2>
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
