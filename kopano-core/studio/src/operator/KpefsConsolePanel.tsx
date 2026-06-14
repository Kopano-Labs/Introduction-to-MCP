import { motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';

interface VectorRow {
  id: string;
  rank?: number;
  metaphor?: string;
  routing_keywords?: string[];
}

interface FlagshipRow {
  sub_brain_id: string;
  display: string;
  catalog_agent: string;
  status: string;
  poc_verdict?: string | null;
}

interface GraduationBar {
  verified_production?: number;
  public_graduation_bar?: number;
  production_bar_met?: boolean;
  public_graduated?: boolean;
  operating_is_not_graduation?: boolean;
  external_swarm?: { receipt_present?: boolean; how_to_log?: string };
  steward_lane?: { brain?: string; teacher?: string; lead_student?: string };
}

interface ClosureStatus {
  internal_kpefs_complete?: boolean;
  external_swarm_receipt?: boolean;
  full_closure?: boolean;
  next_human_step?: string | null;
  external_swarm?: {
    guide?: { cli_template?: string };
  };
}

interface KpefsStatus {
  vectors?: { vectors?: VectorRow[] };
  operating_mesh?: {
    operating_count?: number;
    flagships_total?: number;
    phase3_exit_met?: boolean;
    flagships?: FlagshipRow[];
  };
  graduation_bar?: GraduationBar;
}

interface AiFlowStatus {
  guardian?: { lane?: string };
  identi?: { lane?: string };
  lpm?: { active?: string };
}

const BLASPHEMY_HINT =
  'Sacred caps forbidden for blasphemy register — use oNE_wORLD_oRDER, elon_mask, je, silcon_valley (no honorific caps in brackets).';

export function KpefsConsolePanel() {
  const apiRoot = getApiBase();
  const [kpefs, setKpefs] = useState<KpefsStatus | null>(null);
  const [aiFlow, setAiFlow] = useState<AiFlowStatus | null>(null);
  const [draft, setDraft] = useState('');
  const [lint, setLint] = useState<{ ok?: boolean; violations?: string[] } | null>(null);
  const [route, setRoute] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [promoting, setPromoting] = useState(false);
  const [trusting, setTrusting] = useState(false);
  const [activating, setActivating] = useState(false);
  const [closure, setClosure] = useState<ClosureStatus | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [kRes, aRes, cRes] = await Promise.all([
        fetch(`${apiRoot}/api/kc/phu/kpefs/status`),
        fetch(`${apiRoot}/api/kc/phu/ai-flow/status`),
        fetch(`${apiRoot}/api/kc/phu/closure/status`),
      ]);
      if (!kRes.ok) throw new Error(await kRes.text());
      setKpefs(await kRes.json());
      if (aRes.ok) setAiFlow(await aRes.json());
      if (cRes.ok) setClosure(await cRes.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'KPEFS status failed');
    }
  }, [apiRoot]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runRoute = async () => {
    const res = await fetch(`${apiRoot}/api/kc/phu/kpefs/route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: draft }),
    });
    setRoute(await res.json());
  };

  const onSubmitPreview = async () => {
    const lintRes = await fetch(`${apiRoot}/api/kc/phu/bracket-lint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: draft }),
    });
    const lintBody = await lintRes.json();
    setLint(lintBody);
    if (!lintBody.ok) return;
    await runRoute();
  };

  const vectors = kpefs?.vectors?.vectors ?? [];
  const mesh = kpefs?.operating_mesh;
  const grad = kpefs?.graduation_bar;
  const steward = grad?.steward_lane;

  return (
    <motion.div className="glass-card swarm-mode-card" layout>
      <motion.div className="card-topline" layout>
        <span className="eyebrow">KPEFS four-vector</span>
        <span className={`signal-chip ${mesh?.phase3_exit_met ? 'live' : 'neutral'}`}>
          Mesh {mesh?.operating_count ?? 0}/{mesh?.flagships_total ?? 9}
        </span>
      </motion.div>
      <p className="card-lead">
        Plant → Animal → Homo sapiens → Diaspora. V4 diaspora is a real vector — not a blasphemy agent.
      </p>
      {error && <p className="swarm-footnote">{error}</p>}

      <div className="swarm-agent-grid" style={{ marginBottom: '1rem' }}>
        {vectors.map((v) => (
          <article key={v.id} className="swarm-agent-card">
            <strong>{v.id}</strong>
            <span>{v.metaphor ?? `rank ${v.rank ?? '—'}`}</span>
          </article>
        ))}
      </div>

      <div className="swarm-panel" style={{ marginBottom: '1rem' }}>
        <h4>Operating mesh (Phase 3)</h4>
        <p className="swarm-footnote">
          {mesh?.phase3_exit_met
            ? 'All flagships operating with PoC PASS.'
            : 'Promote via god mode or CLI: python scripts/kc_phu_operating_mesh.py promote-all'}
        </p>
        <ul className="swarm-checklist">
          {(mesh?.flagships ?? []).map((f) => (
            <li key={f.sub_brain_id} className={f.status === 'operating' ? 'ok' : ''}>
              {f.display} — {f.status}
              {f.poc_verdict ? ` · PoC ${f.poc_verdict}` : ''}
            </li>
          ))}
        </ul>
      </div>

      <div className="swarm-panel" style={{ marginBottom: '1rem' }}>
        <h4>Graduation bar (Phase 5)</h4>
        <p className="swarm-footnote">
          Verified production {grad?.verified_production ?? '…'}/{grad?.public_graduation_bar ?? 10}
          {' '}
          — {grad?.production_bar_met ? 'bar met' : 'not graduated yet'}.
          Operating mesh ≠ public graduation.
        </p>
        {steward && (
          <p className="swarm-footnote">
            {steward.brain?.toUpperCase()} · teacher {steward.teacher} · lead student {steward.lead_student}
          </p>
        )}
        <p className="swarm-footnote">
          External swarm (CMD-03): {grad?.external_swarm?.receipt_present ? 'receipt on file' : 'manual kimi_ack required'}
        </p>
      </div>

      {closure && (
        <div className="swarm-panel" style={{ marginBottom: '1rem' }}>
          <h4>Closure</h4>
          <p className="swarm-footnote">
            Internal KPEFS: {closure.internal_kpefs_complete ? 'complete' : 'open'} · External receipt:{' '}
            {closure.external_swarm_receipt ? 'yes' : 'pending'} · Full closure:{' '}
            {closure.full_closure ? 'yes' : 'no'}
          </p>
          {closure.next_human_step && (
            <p className="swarm-footnote">{closure.next_human_step}</p>
          )}
          {closure.external_swarm?.guide?.cli_template && (
            <code className="swarm-cli-block">{closure.external_swarm.guide.cli_template}</code>
          )}
        </div>
      )}

      {aiFlow && (
        <div className="swarm-panel" style={{ marginBottom: '1rem' }}>
          <h4>AI flows</h4>
          <p className="swarm-footnote">
            Guardian: {aiFlow.guardian?.lane ?? 'KC Save|Watch + Cassy'} · Identi:{' '}
            {aiFlow.identi?.lane ?? 'LPM/LPH — no KC teacher_review write'}
          </p>
        </div>
      )}

      <label className="field-shell">
        <span>Draft (bracket lint + vector route)</span>
        <textarea rows={4} value={draft} onChange={(e) => setDraft(e.target.value)} />
      </label>
      <p className="swarm-footnote">{BLASPHEMY_HINT}</p>
      {lint && (
        <p className={`swarm-footnote ${lint.ok ? '' : 'warn'}`}>
          Bracket lint: {lint.ok ? 'OK' : (lint.violations ?? []).join('; ')}
        </p>
      )}
      {route && (
        <p className="swarm-footnote">
          Route: {(route as { active_vector?: string }).active_vector ?? '—'} ·{' '}
          {(route as { department_hint?: string }).department_hint ?? ''}
        </p>
      )}
      <div className="button-row">
        <button type="button" className="action-button primary" onClick={() => { void onSubmitPreview(); }}>
          Lint + route
        </button>
        <button type="button" className="action-button ghost" onClick={() => { void refresh(); }}>
          Refresh
        </button>
        <button
          type="button"
          className="action-button ghost"
          disabled={promoting}
          onClick={() => {
            setPromoting(true);
            fetch(`${apiRoot}/api/kc/phu/operating-mesh/promote-all`, { method: 'POST' })
              .then((r) => r.json())
              .then(() => { void refresh(); })
              .catch((err) => setError(String(err)))
              .finally(() => setPromoting(false));
          }}
        >
          {promoting ? 'Promoting…' : 'Promote all (god)'}
        </button>
        <button
          type="button"
          className="action-button ghost"
          disabled={trusting}
          onClick={() => {
            setTrusting(true);
            fetch(`${apiRoot}/api/kc/phu/graduation-bar/steward-trust`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ note: 'Studio steward trust — KC Cassey students' }),
            })
              .then((r) => r.json())
              .then(() => { void refresh(); })
              .catch((err) => setError(String(err)))
              .finally(() => setTrusting(false));
          }}
        >
          {trusting ? 'Logging…' : 'Steward trust receipt'}
        </button>
        <button
          type="button"
          className="action-button primary"
          disabled={activating}
          onClick={() => {
            setActivating(true);
            fetch(`${apiRoot}/api/kc/phu/steward-lane/activate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                note: 'KC+Cassy steward lane — lead dev run',
              }),
            })
              .then((r) => r.json())
              .then(() => { void refresh(); })
              .catch((err) => setError(String(err)))
              .finally(() => setActivating(false));
          }}
        >
          {activating ? 'Activating…' : 'Activate KC + Cassy'}
        </button>
      </div>
    </motion.div>
  );
}
