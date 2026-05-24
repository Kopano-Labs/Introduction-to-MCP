import { motion } from 'framer-motion';
import { useState } from 'react';
import { useOperator } from './OperatorProvider';

const PROOF_ACTIONS = ['jsonl_validate', 'proof_check', 'guard_all', 'production_verify'] as const;
const CASSY_ACTIONS = ['cassy_activate_seed', 'cassy_wit_promote', 'apprenticeship_promote', 'swarm_bootstrap'] as const;
const PHU_ACTIONS = ['phu_reattach_subbrains', 'phu_populate_main_brain'] as const;
const GIT_ACTIONS = ['git_status', 'git_fetch', 'git_pull_ff', 'git_push'] as const;

export function GodModeDock() {
  const {
    isGodMode,
    user,
    overview,
    lastOutput,
    busy,
    error,
    signIn,
    signOut,
    refreshOverview,
    runAction,
    runGit,
  } = useOperator();

  const [open, setOpen] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  if (!isGodMode && !open) {
    return (
      <button type="button" className="god-dock-tab" onClick={() => setOpen(true)}>
        Cassy · God
      </button>
    );
  }

  return (
    <motion.aside
      className={`god-dock ${open ? 'open' : 'collapsed'}`}
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <header className="god-dock-head">
        <div>
          <span className="eyebrow">Cassy lane · Super God</span>
          <strong>{user?.email ?? 'Monorepo control'}</strong>
          <span className="god-dock-sub">
            {overview?.persona_route ?? 'Cassy (student) → Cassey (teacher) · KC (ledger)'}
          </span>
        </div>
        <button type="button" className="action-button ghost" onClick={() => setOpen((v) => !v)}>
          {open ? 'Hide' : 'Show'}
        </button>
      </header>

      {open && !isGodMode && (
        <section className="god-dock-panel">
          <p>Sign in once — controls the whole PWA and monorepo scripts.</p>
          <label className="field-shell">
            <span>Email</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="field-shell">
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <button
            type="button"
            className="action-button primary"
            disabled={busy}
            onClick={() => { void signIn(email, password); }}
          >
            {busy ? 'Signing in…' : 'Unlock Super God'}
          </button>
        </section>
      )}

      {open && isGodMode && (
        <>
          <section className="god-dock-stats">
            <article>
              <span>Branch</span>
              <strong>{overview?.git?.branch ?? '…'}</strong>
            </article>
            <article>
              <span>Proof bar</span>
              <strong>{overview?.proof_bar_pass ? 'PASS' : 'OPEN'}</strong>
            </article>
            <article>
              <span>Cassy</span>
              <strong>{overview?.cassy?.display_name ?? 'Cassy'}</strong>
            </article>
          </section>

          <section className="god-dock-panel">
            <h4>Proof · monorepo</h4>
            <div className="god-dock-actions">
              {PROOF_ACTIONS.map((id) => (
                <button key={id} type="button" className="action-button ghost" disabled={busy} onClick={() => { void runAction(id); }}>
                  {id}
                </button>
              ))}
            </div>
          </section>

          <section className="god-dock-panel">
            <h4>Kopano-Phu · Bracket Protocol</h4>
            <div className="god-dock-actions">
              {PHU_ACTIONS.map((id) => (
                <button
                  key={id}
                  type="button"
                  className="action-button primary"
                  disabled={busy}
                  onClick={() => { void runAction(id, id === 'phu_populate_main_brain'); }}
                >
                  {id}
                </button>
              ))}
            </div>
          </section>

          <section className="god-dock-panel">
            <h4>Cassy stewards</h4>
            <div className="god-dock-actions">
              {CASSY_ACTIONS.map((id) => (
                <button
                  key={id}
                  type="button"
                  className="action-button primary"
                  disabled={busy}
                  onClick={() => { void runAction(id, true); }}
                >
                  {id}
                </button>
              ))}
            </div>
          </section>

          <section className="god-dock-panel">
            <h4>Git</h4>
            <div className="god-dock-actions">
              {GIT_ACTIONS.map((id) => (
                <button
                  key={id}
                  type="button"
                  className="action-button ghost"
                  disabled={busy}
                  onClick={() => { void runGit(id, id === 'git_push'); }}
                >
                  {id}
                </button>
              ))}
            </div>
          </section>

          <section className="god-dock-output">
            <div className="god-dock-output-head">
              <strong>Last receipt</strong>
              <button type="button" className="action-button ghost" disabled={busy} onClick={() => { void refreshOverview(); }}>
                Refresh
              </button>
              <button type="button" className="action-button ghost" onClick={signOut}>
                Sign out
              </button>
            </div>
            <pre>{lastOutput || 'Run a Cassy or proof action — output lands here.'}</pre>
          </section>
        </>
      )}

      {error && <p className="god-dock-error">{error}</p>}
    </motion.aside>
  );
}
