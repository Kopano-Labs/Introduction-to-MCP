import { motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';
import type { FeedLogEntry, LabsAnalytics, McpConsoleReply } from '../types';

type ConsoleMode = 'context' | 'swarm' | 'proof' | 'ci';

interface SwarmAgent {
  id: string;
  display_name?: string;
  role: string;
  lane?: string;
  swarm_slot?: string;
  apprenticeship?: { student?: string; teacher?: string; brain?: string };
}

interface CassyRole {
  id: string;
  display_name: string;
  role: string;
  lead_student: string;
  teacher: string;
  brain: string;
  mission: string;
  wit_band: string;
  drill_promoted_local: number | null;
  drill_is_not_graduation: boolean;
  console_role: string;
  steward_commands: string[];
}

interface SwarmConsoleStatus {
  persona_route: string;
  composer_hint?: string;
  cassy?: CassyRole;
  context_host: string;
  proof_bar_pass: boolean;
  proof_gaps: string[];
  git: {
    branch: string;
    head_sha: string;
    upstream: string | null;
    ahead: number;
    behind: number;
    origin_fetch_url: string;
    warnings: string[];
  };
  checks: {
    jsonl_validate_ok: boolean;
    proof_check_ok: boolean;
    guard_all_ok: boolean;
  };
  doctrine: {
    verified_production: number;
    production_bar_met: boolean;
    roadmap_gate_met: boolean;
    swarm_ack_met: boolean;
    public_graduation_bar: number;
  };
  ci: {
    workflow: string;
    actions_url: string;
    compare_url: string;
    guard_command: string;
  };
  cli: string[];
}

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

const apiRoot = getApiBase();

const modeLabels: Record<ConsoleMode, string> = {
  context: 'Context',
  swarm: 'Swarm',
  proof: 'Proof',
  ci: 'CI',
};

const modeIcons: Record<ConsoleMode, string> = {
  context: '⌘',
  swarm: '◎',
  proof: '✓',
  ci: '∿',
};

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
  const [mode, setMode] = useState<ConsoleMode>('context');
  const [status, setStatus] = useState<SwarmConsoleStatus | null>(null);
  const [agents, setAgents] = useState<SwarmAgent[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refreshStatus = useCallback(async () => {
    try {
      const [statusRes, agentsRes] = await Promise.all([
        fetch(`${apiRoot}/api/kc/swarm-console/status`),
        fetch(`${apiRoot}/api/kc/swarm-agents`),
      ]);
      if (statusRes.ok) {
        setStatus(await statusRes.json());
      } else {
        setLoadError(await statusRes.text());
      }
      if (agentsRes.ok) {
        const body = await agentsRes.json();
        setAgents(body.agents ?? []);
      }
      setLoadError(null);
    } catch {
      setLoadError('Swarm Console API unreachable — start kopano-core API locally.');
    }
  }, []);

  useEffect(() => {
    void refreshStatus();
  }, [refreshStatus]);

  const modelOptions = consoleReply?.model_options ?? [
    { id: 'deterministic', label: 'deterministic fallback', model: 'deterministic-fallback' },
  ];

  const badgeClass = (ok: boolean | undefined, warn?: boolean) => {
    if (ok) return 'swarm-badge ok';
    if (warn) return 'swarm-badge warn';
    return 'swarm-badge err';
  };

  const meshAgents = agents.filter((a) => a.role === 'mesh' || a.swarm_slot);
  const teacherAgent = agents.find((a) => a.id === 'cassey');
  const cassy = status?.cassy;

  return (
    <motion.div
      className="swarm-console"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.45 }}
    >
      <aside className="swarm-rail" aria-label="Console modes">
        <motion.div className="swarm-brand" layout>KC</motion.div>
        {(Object.keys(modeLabels) as ConsoleMode[]).map((key) => (
          <button
            key={key}
            type="button"
            className={`swarm-rail-btn ${mode === key ? 'active' : ''}`}
            title={modeLabels[key]}
            onClick={() => setMode(key)}
          >
            {modeIcons[key]}
          </button>
        ))}
      </aside>

      <aside className="swarm-sidebar">
        <motion.div className="swarm-workspace swarm-cassy-card" layout>
          <span className="swarm-dot live" />
          <motion.div layout>
            <strong>{cassy?.display_name ?? 'Cassy'} · lead student</strong>
            <span>{status?.persona_route ?? 'Cassy → Cassey · KC'}</span>
            {cassy?.mission && <span className="swarm-cassy-mission">{cassy.mission}</span>}
          </motion.div>
        </motion.div>

        {cassy && (
          <motion.div className="swarm-panel swarm-cassy-stats" layout>
            <h4>Cassy here</h4>
            <p>{cassy.console_role}</p>
            <p className="swarm-footnote">
              Drill promoted (local): {cassy.drill_promoted_local ?? '—'} — not graduation.
              Verified prod: {status?.doctrine.verified_production ?? '…'}.
            </p>
          </motion.div>
        )}

        <div className="swarm-block">
          <h3>Modes</h3>
          <nav className="swarm-nav">
            {(Object.keys(modeLabels) as ConsoleMode[]).map((key) => (
              <button
                key={key}
                type="button"
                className={`swarm-nav-item ${mode === key ? 'active' : ''}`}
                onClick={() => setMode(key)}
              >
                <span>{modeIcons[key]} {modeLabels[key]}</span>
                {key === 'proof' && status && (
                  <span className={badgeClass(status.proof_bar_pass)}>
                    {status.proof_bar_pass ? 'PASS' : `${status.proof_gaps.length} gaps`}
                  </span>
                )}
                {key === 'ci' && status && (
                  <span className={badgeClass(status.checks.guard_all_ok)}>
                    {status.checks.guard_all_ok ? 'Ready' : 'Check'}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="swarm-block">
          <h3>Connectors</h3>
          <div className="swarm-nav">
            <motion.div className="swarm-nav-item static" layout>
              <span>⌁ Web / research</span>
              <span className="swarm-badge ok">BFF</span>
            </motion.div>
            <motion.div className="swarm-nav-item static" layout>
              <span>⌘ Git / GitHub</span>
              <span className={badgeClass(Boolean(status?.git.origin_fetch_url))}>
                {status?.git.origin_fetch_url ? 'Bound' : '…'}
              </span>
            </motion.div>
            <motion.div className="swarm-nav-item static" layout>
              <span>⟲ JSONL ledger</span>
              <span className={badgeClass(status?.checks.jsonl_validate_ok)}>Validate</span>
            </motion.div>
            <motion.div className="swarm-nav-item static" layout>
              <span>⬡ Swarm receipts</span>
              <span className={badgeClass(status?.doctrine.swarm_ack_met, !status?.doctrine.swarm_ack_met)}>
                {status?.doctrine.swarm_ack_met ? 'ACK' : 'Manual'}
              </span>
            </motion.div>
          </div>
        </div>

        <motion.div className="swarm-panel" layout>
          <h4>Servitude Triad</h4>
          <p>Grit + Realism + Aesthetics — unified. Drill promoted ≠ graduation.</p>
          <button type="button" className="action-button ghost" onClick={() => { void refreshStatus(); }}>
            Refresh proof strip
          </button>
        </motion.div>
      </aside>

      <main className="swarm-main">
        <header className="swarm-main-head">
          <div>
            <span className="eyebrow">KC Swarm Console</span>
            <h2>{modeLabels[mode]}</h2>
            <p>
              One composer · server-mediated tools · receipts before “complete”.
              {loadError && ` ${loadError}`}
            </p>
          </div>
          <div className="badge-cluster">
            <span className={`status-badge ${status?.proof_bar_pass ? 'live' : 'neutral'}`}>
              Proof bar: {status?.proof_bar_pass ? 'PASS' : 'OPEN'}
            </span>
            <span className="status-badge neutral">
              Verified prod: {status?.doctrine.verified_production ?? '…'} / {status?.doctrine.public_graduation_bar ?? 10}
            </span>
          </div>
        </header>

        <section className="swarm-center">
          {mode === 'context' && (
            <div className="swarm-context-grid">
              <motion.article className="glass-card console-composer" layout>
                <motion.div className="card-topline" layout>
                  <span className="eyebrow">Compose</span>
                  <span className="signal-chip live">MCP</span>
                </motion.div>
                <p className="card-lead">
                  Teacher <strong>Cassey</strong> · lead student <strong>Cassy</strong> · brain <strong>KC</strong> (ledger only).
                  {status?.composer_hint ? ` ${status.composer_hint}` : ''}
                </p>
                <label className="field-shell">
                  <span>Model</span>
                  <select value={selectedModel} onChange={(e) => onModelChange(e.target.value)}>
                    {modelOptions.map((option) => (
                      <option key={option.id} value={option.id}>{option.label}</option>
                    ))}
                  </select>
                </label>
                <label className="field-shell">
                  <span>Prompt</span>
                  <textarea
                    rows={5}
                    value={consoleMessage}
                    onChange={(e) => onConsoleMessageChange(e.target.value)}
                  />
                </label>
                <motion.div className="swarm-tool-row" layout>
                  {['Web', 'Fetch', 'Git', 'Swarm', 'Proof'].map((chip) => (
                    <span key={chip} className="swarm-tool-chip">{chip}</span>
                  ))}
                </motion.div>
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
                <h3>{consoleReply?.model_used ?? 'No response'}</h3>
                <div className="console-output-panel tall">
                  <p>{consoleStream || consoleReply?.response || 'Send a bounded prompt — tools-first, cite evidence.'}</p>
                </div>
              </motion.article>
            </div>
          )}

          {mode === 'swarm' && (
            <motion.div className="glass-card swarm-mode-card" layout>
              <motion.div className="card-topline" layout>
                <span className="eyebrow">Swarm dispatch</span>
                <span className="signal-chip live">Cassy binds all agents</span>
              </motion.div>
              {cassy && (
                <article className="swarm-agent-card swarm-agent-card-lead">
                  <strong>{cassy.display_name}</strong>
                  <span>{cassy.role} — {cassy.wit_band || 'WIT diaspora band'}</span>
                  <p className="swarm-footnote">{cassy.console_role}</p>
                </article>
              )}
              <p className="card-lead">
                External Kimi/swarm = <strong>manual-execution-required</strong>. Mesh slots inherit
                {' '}
                <code>apprenticeship.student=cassy</code> — corporate names are not Cassy&apos;s ceiling.
              </p>
              {teacherAgent && (
                <p className="swarm-footnote">
                  Teacher <strong>{teacherAgent.display_name ?? teacherAgent.id}</strong>
                  {' '}
                  ({teacherAgent.role}) writes <code>teacher_review</code>.
                </p>
              )}
              <div className="swarm-agent-grid">
                {meshAgents.map((agent) => (
                  <article key={agent.id} className="swarm-agent-card">
                    <strong>{agent.display_name ?? agent.id}</strong>
                    <span>{agent.role}{agent.swarm_slot ? ` · slot ${agent.swarm_slot}` : ''}</span>
                  </article>
                ))}
              </div>
              {cassy?.steward_commands && (
                <motion.div className="swarm-cli-block">
                  {cassy.steward_commands.map((cmd) => (
                    <code key={cmd}>{cmd}</code>
                  ))}
                </motion.div>
              )}
            </motion.div>
          )}

          {mode === 'proof' && status && (
            <motion.div className="glass-card swarm-mode-card" layout>
              <motion.div className="card-topline" layout>
                <span className="eyebrow">Proof validator</span>
                <span className={badgeClass(status.proof_bar_pass)}>
                  {status.proof_bar_pass ? 'PASS' : 'GAPS'}
                </span>
              </motion.div>
              <ul className="swarm-checklist">
                <li className={status.checks.jsonl_validate_ok ? 'ok' : 'fail'}>
                  JSONL validate — exit {status.checks.jsonl_validate_ok ? '0' : '≠0'}
                </li>
                <li className={status.checks.proof_check_ok ? 'ok' : 'fail'}>
                  proof-check — exit {status.checks.proof_check_ok ? '0' : '≠0'}
                </li>
                <li className={status.doctrine.production_bar_met ? 'ok' : 'fail'}>
                  Verified production {status.doctrine.verified_production} (min {status.doctrine.public_graduation_bar})
                </li>
                <li className={status.doctrine.roadmap_gate_met ? 'ok' : 'fail'}>
                  Main Brain roadmap entry gate
                </li>
                <li className={status.checks.guard_all_ok ? 'ok' : 'fail'}>
                  kc_guard all (production + roadmap)
                </li>
                <li className={status.doctrine.swarm_ack_met ? 'ok' : 'warn'}>
                  External swarm ACK {status.doctrine.swarm_ack_met ? 'present' : 'optional / manual'}
                </li>
              </ul>
              {status.proof_gaps.length > 0 && (
                <div className="swarm-gaps">
                  <strong>Actionable gaps</strong>
                  <ul>
                    {status.proof_gaps.map((gap) => (
                      <li key={gap}>{gap}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="swarm-cli-block">
                {(status.cli ?? []).map((cmd) => (
                  <code key={cmd}>{cmd}</code>
                ))}
              </div>
            </motion.div>
          )}

          {mode === 'ci' && status && (
            <motion.div className="glass-card swarm-mode-card" layout>
              <div className="card-topline">
                <span className="eyebrow">CI enforcer</span>
                <span className="signal-chip live">GHA</span>
              </div>
              <p className="card-lead">
                Workflow: <code>{status.ci.workflow}</code> · job <strong>swarm-jsonl</strong>
              </p>
              <div className="button-row">
                <a className="action-button primary" href={status.ci.actions_url} target="_blank" rel="noreferrer">
                  Open Actions
                </a>
                <a className="action-button ghost" href={status.ci.compare_url} target="_blank" rel="noreferrer">
                  Compare branch
                </a>
              </div>
              <pre className="swarm-ci-pre">{status.ci.guard_command}</pre>
              <p className="swarm-footnote">
                Requests: {labsAnalytics?.mcp_console.requests ?? 0} ·
                Sessions: {labsAnalytics?.mcp_console.sessions ?? 0}
              </p>
            </motion.div>
          )}
        </section>

        <motion.section className="glass-card relay-card swarm-relay" layout>
          <div className="card-topline">
            <span className="eyebrow">Council relay</span>
            <span className="signal-chip neutral">{feedPreview.length} signals</span>
          </div>
          <div className="timeline-list">
            {feedPreview.slice(0, 3).map((entry) => (
              <article key={entry.id} className="timeline-item">
                <div className="timeline-meta">
                  <span>{entry.agent?.toUpperCase() ?? entry.type}</span>
                  <span>{new Date(entry.received_at).toLocaleTimeString()}</span>
                </div>
                <p>{entry.content ?? entry.reasoning ?? 'Event captured.'}</p>
              </article>
            ))}
          </div>
        </motion.section>
      </main>

      <aside className="swarm-right">
        <motion.div className="glass-card swarm-right-card" layout>
          <h3>Git sync</h3>
          {status ? (
            <>
              <p><strong>{status.git.branch}</strong> @ {status.git.head_sha}</p>
              <p>{status.git.ahead} ahead · {status.git.behind} behind</p>
              {status.git.warnings.map((w) => (
                <p key={w} className="swarm-warn">{w}</p>
              ))}
            </>
          ) : (
            <p>Loading…</p>
          )}
        </motion.div>

        <motion.div className="glass-card swarm-right-card" layout>
          <h3>Proof strip</h3>
          <p>Validate: {status?.checks.jsonl_validate_ok ? 'OK' : 'FAIL'}</p>
          <p>Proof-check: {status?.checks.proof_check_ok ? 'OK' : 'FAIL'}</p>
          <p>Roadmap gate: {status?.doctrine.roadmap_gate_met ? 'OK' : 'OPEN'}</p>
        </motion.div>

        <motion.div className="glass-card swarm-right-card" layout>
          <h3>Mark complete</h3>
          <p className="swarm-footnote">
            Disabled until doctrine satisfied — mirror kc_guard, not chat theater.
          </p>
          <button type="button" className="action-button primary" disabled={!status?.proof_bar_pass}>
            Proof bar PASS required
          </button>
        </motion.div>
      </aside>
    </motion.div>
  );
}
