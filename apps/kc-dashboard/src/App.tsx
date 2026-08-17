import { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import registry from "../../../governance/kpgs-vnext/kc/sub-membrane-registry.json";
import dashboardState from "../../../governance/kpgs-vnext/kc/dashboard-state.json";

type Membrane = (typeof registry.sub_membranes)[number];

const authorityLabel: Record<Membrane["authority"], string> = {
  canonical: "Canonical",
  reference: "Reference",
  experimental: "Experimental",
  "external-reference": "External ref",
};

function shortSha(sha: string | null) {
  return sha ? sha.slice(0, 9) : "PIN PENDING";
}

export default function App() {
  const reduceMotion = useReducedMotion();
  const [selectedId, setSelectedId] = useState("canonical-introduction-to-mcp");
  const selected = useMemo(
    () => registry.sub_membranes.find((item) => item.id === selectedId) ?? registry.sub_membranes[0],
    [selectedId],
  );
  const pinned = registry.sub_membranes.filter((item) => item.revision).length;

  return (
    <main className="shell">
      <header className="topbar">
        <div className="identity">
          <div className="kc-mark" aria-hidden="true">KC</div>
          <div>
            <p className="eyebrow">KPGS · SEAT 01 · STATEFUL</p>
            <h1>Observer / Landlord</h1>
          </div>
        </div>
        <div className="snapshot" aria-label="Dashboard freshness">
          <span className="pulse" aria-hidden="true" />
          SNAPSHOT · 17 AUG 2026
        </div>
      </header>

      <section className="context-lock" aria-labelledby="context-title">
        <div>
          <p className="eyebrow" id="context-title">CONTEXT_SOURCE_LOCK</p>
          <strong>{dashboardState.context_lock.source}</strong>
        </div>
        <p>{dashboardState.context_lock.boundary}</p>
        <span className="priority">{dashboardState.context_lock.urgency}</span>
      </section>

      <section className="metrics" aria-label="KC estate metrics">
        <Metric label="Sub-Membranes" value={String(registry.sub_membranes.length)} note="weekend seed" />
        <Metric label="Pinned heads" value={`${pinned}/13`} note="provenance observed" />
        <Metric label="Canonical" value="1" note="Introduction-to-MCP" />
        <Metric label="KC authority" value="READ" note="observe · correlate · publish" />
      </section>

      <section className="workspace">
        <div className="topology-card panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SUB-MEMBRANE ESTATE</p>
              <h2>KC sees the system as one governed landscape.</h2>
            </div>
            <span className="status-chip">13 SEEDED</span>
          </div>

          <div className="topology" aria-label="KC Sub-Membrane topology">
            <motion.div
              className="kc-core"
              initial={reduceMotion ? false : { opacity: 0, scale: 0.92 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.45 }}
            >
              <span>KC</span>
              <small>LANDLORD</small>
            </motion.div>

            <div className="membrane-grid">
              {registry.sub_membranes.map((membrane, index) => (
                <motion.button
                  type="button"
                  key={membrane.id}
                  className={`membrane-node ${membrane.authority} ${selectedId === membrane.id ? "selected" : ""}`}
                  onClick={() => setSelectedId(membrane.id)}
                  initial={reduceMotion ? false : { opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.32, delay: reduceMotion ? 0 : Math.min(index * 0.035, 0.3) }}
                  aria-pressed={selectedId === membrane.id}
                >
                  <span className="node-dot" aria-hidden="true" />
                  <strong>{membrane.repository.replace("RobynAwesome/", "")}</strong>
                  <small>{authorityLabel[membrane.authority]}</small>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        <aside className="inspector panel" aria-live="polite">
          <p className="eyebrow">SELECTED MEMBRANE</p>
          <h2>{selected.repository}</h2>
          <div className="badge-row">
            <span className={`badge ${selected.authority}`}>{authorityLabel[selected.authority]}</span>
            <span className="badge neutral">{selected.ingestion_state}</span>
          </div>
          <dl>
            <div><dt>Branch</dt><dd>{selected.default_branch}</dd></div>
            <div><dt>Revision</dt><dd className="mono">{shortSha(selected.revision)}</dd></div>
            <div><dt>Semantic state</dt><dd>{selected.semantic_state}</dd></div>
          </dl>
          <p className="inspector-note">{selected.notes}</p>
          <div className="facet-list">
            {selected.logic_facets.map((facet) => <span key={facet}>{facet}</span>)}
          </div>
        </aside>
      </section>

      <section className="lower-grid">
        <div className="panel">
          <div className="panel-heading compact"><div><p className="eyebrow">UNRESOLVED GATES</p><h2>KC does not hide the blocker.</h2></div></div>
          <div className="gate-list">
            {dashboardState.gates.map((gate) => (
              <article className="gate" key={gate.id}>
                <span className={`severity ${gate.severity.toLowerCase()}`}>{gate.severity}</span>
                <div><strong>{gate.label}</strong><small>{gate.owner}</small></div>
                <span className="open-state">{gate.status}</span>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading compact"><div><p className="eyebrow">FRONTIER LANES</p><h2>Rent capability. Keep sovereignty.</h2></div></div>
          <div className="lane-list">
            {dashboardState.frontier_lanes.map((lane) => (
              <article className="lane" key={lane.id}>
                <div><strong>{lane.label}</strong><small>{lane.role}</small></div>
                <div className="lane-state"><span>{lane.version}</span><b>{lane.state}</b></div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="authority panel">
        <div><p className="eyebrow">AUTHORITY BOUNDARY</p><h2>KC knows more now. KC does not own more.</h2></div>
        <div className="authority-columns">
          <div><strong>KC MAY</strong><p>Observe · correlate · publish context · surface urgency · map provenance · point to receipts.</p></div>
          <div><strong>KC HANDS OFF</strong><p>APEX orchestrates · KHELOS validates · renters execute scoped capabilities · humans retain human authority.</p></div>
        </div>
      </section>

      <footer>
        <span>TypeScript 7 · React 19 · Vite 8</span>
        <span>SNAPSHOT ≠ REALTIME · SUB-MEMBRANE ≠ CANONICAL AUTHORITY</span>
      </footer>
    </main>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return <article className="metric panel"><p className="eyebrow">{label}</p><strong>{value}</strong><small>{note}</small></article>;
}
