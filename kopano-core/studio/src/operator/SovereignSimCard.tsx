import { motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';

interface TriadActor {
  mode?: string;
  role?: string;
  executes?: boolean;
  active?: boolean;
  host?: string;
}

interface WorldRegion {
  region_id: string;
  kind: string;
  domain?: string;
  codename?: string;
  status?: string;
  agent_count?: number;
  landlord_agent?: string;
  pavement_target?: string;
}

interface SovereignSimUi {
  activation_allowed?: boolean;
  gate_verdict?: string;
  behavioral_poc_verdict?: string;
  behavioral_measurand?: { observed?: number; unit?: string; baseline?: number };
  failed_behavioral_proofs?: string[];
  kopano_context?: { host?: string; api_mount?: string };
  triad?: {
    kc?: TriadActor;
    cassy?: TriadActor;
    cassey?: TriadActor;
    kopano?: TriadActor;
  };
  agent_total?: number;
  regions?: WorldRegion[];
  steward_lane?: { active?: boolean };
}

export function SovereignSimCard() {
  const [ui, setUi] = useState<SovereignSimUi | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [booting, setBooting] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/kc/phu/sovereign-sim/ui`);
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setUi(await res.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sovereign sim API failed');
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runSmoke = async () => {
    setBooting(true);
    try {
      const res = await fetch(`${getApiBase()}/api/kc/phu/kpgs/smoke-poc`, { method: 'POST' });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Smoke PoC failed');
    } finally {
      setBooting(false);
    }
  };

  const gateOk = ui?.activation_allowed;
  const triad = ui?.triad;

  return (
    <motion.div className="swarm-panel swarm-phu-card" layout>
      <h4>Sovereign SIM · KPGS hood</h4>
      <p className="swarm-footnote">
        Kopano Context GUI — thesis world-building gated on 300-agent guild.
      </p>
      <div className="swarm-phu-metrics">
        <span className={gateOk ? 'swarm-badge ok' : 'swarm-badge err'}>
          Gate {ui?.gate_verdict ?? '…'}
        </span>
        <span className="swarm-badge neutral">
          {ui?.agent_total ?? 0} agents
        </span>
        <span className={ui?.steward_lane?.active ? 'swarm-badge ok' : 'swarm-badge warn'}>
          Steward {ui?.steward_lane?.active ? 'ACTIVE' : 'idle'}
        </span>
        <span className={ui?.behavioral_poc_verdict === 'PASS' ? 'swarm-badge ok' : 'swarm-badge warn'}>
          Behavioral {ui?.behavioral_poc_verdict ?? '…'}
        </span>
      </div>
      {ui?.behavioral_measurand && (
        <p className="swarm-footnote">
          PoC Δ: {ui.behavioral_measurand.baseline ?? 0} → {ui.behavioral_measurand.observed ?? 0}{' '}
          {ui.behavioral_measurand.unit ?? 'dispatch_proceed'} (independent instrument)
        </p>
      )}
      <div className="swarm-footnote">
        <strong>KC</strong> {triad?.kc?.mode ?? 'Save|Watch'} ·{' '}
        <strong>Cassy</strong> {triad?.cassy?.mode ?? 'execute'} ·{' '}
        <strong>Context</strong> {ui?.kopano_context?.host ?? 'context.kopanolabs.com'}
      </div>
      {ui?.regions && ui.regions.length > 0 && (
        <ul className="swarm-footnote" style={{ marginTop: '0.5rem', paddingLeft: '1rem' }}>
          {ui.regions.slice(0, 5).map((r) => (
            <li key={r.region_id}>
              {r.codename ?? r.domain ?? r.region_id}
              {r.agent_count != null ? ` · ${r.agent_count} agents` : ''}
            </li>
          ))}
        </ul>
      )}
      <div className="god-dock-actions">
        <button type="button" className="action-button ghost" onClick={() => { void refresh(); }}>
          Refresh sim
        </button>
        <button
          type="button"
          className="action-button primary"
          disabled={booting}
          onClick={() => { void runSmoke(); }}
        >
          {booting ? 'Running smoke…' : 'KPGS smoke PoC'}
        </button>
      </div>
      {error && <p className="god-dock-error">{error}</p>}
    </motion.div>
  );
}
