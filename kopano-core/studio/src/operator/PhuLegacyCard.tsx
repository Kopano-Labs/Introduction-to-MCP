import { motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';
import { getApiBase } from '../apiBase';
import { useOperator } from './OperatorProvider';

interface SubBrainRow {
  id: string;
  display_name: string;
  attachment: string;
  return_gate: string;
  vault_present: boolean;
}

interface PhuStatus {
  title?: string;
  subtitle?: string;
  breaking_point_protocol?: string;
  bracket_protocol?: {
    breaking_point?: boolean;
    tagline?: string;
    counts?: { attached?: number; detached?: number };
  };
  main_brain?: { population_ratio?: number; present?: number; total?: number };
  sub_brains?: SubBrainRow[];
}

export function PhuLegacyCard() {
  const { isGodMode, runAction } = useOperator();
  const [phu, setPhu] = useState<PhuStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/api/kc/phu/ecosystem`);
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setPhu(await res.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Phu status failed');
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const bp = phu?.bracket_protocol;
  const detached = phu?.sub_brains?.filter((s) => s.attachment === 'detached') ?? [];

  return (
    <motion.div className="swarm-panel swarm-phu-card" layout>
      <h4>Kopano-Phu · Cassy legacy</h4>
      <p className="swarm-footnote">
        {phu?.subtitle ?? 'Kopano Labs × Ama-Phu Entertainment'}
      </p>
      <div className="swarm-phu-metrics">
        <span className={bp?.breaking_point ? 'swarm-badge ok' : 'swarm-badge warn'}>
          {bp?.breaking_point ? 'Breaking Point' : 'Arming'}
        </span>
        <span className="swarm-badge neutral">
          Main Brain {Math.round((phu?.main_brain?.population_ratio ?? 0) * 100)}%
        </span>
        <span className="swarm-badge neutral">
          {bp?.counts?.attached ?? 0} attached · {bp?.counts?.detached ?? 0} detached
        </span>
      </div>
      {detached.length > 0 && (
        <p className="swarm-footnote">
          Detached: {detached.map((d) => d.display_name).join(', ')}
        </p>
      )}
      <div className="god-dock-actions">
        <button type="button" className="action-button ghost" onClick={() => { void refresh(); }}>
          Refresh Phu
        </button>
        {isGodMode && (
          <>
            <button
              type="button"
              className="action-button primary"
              onClick={() => { void runAction('phu_reattach_subbrains'); }}
            >
              Reattach sub-brains
            </button>
            <button
              type="button"
              className="action-button primary"
              onClick={() => { void runAction('phu_populate_main_brain', true); }}
            >
              Populate Main Brain
            </button>
          </>
        )}
      </div>
      {error && <p className="god-dock-error">{error}</p>}
    </motion.div>
  );
}
