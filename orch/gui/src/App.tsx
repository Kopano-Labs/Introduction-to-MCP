import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface ReasoningBlock {
  block_id: string;
  agent: string;
  role: string | null;
  content: string;
  reasoning: string;
  value_score: number;
  override_score: number | null;
  improvement_hint: string | null;
  is_student: number;
}

interface Round {
  id: string;
  round_number: number;
  blocks: ReasoningBlock[];
}

interface Lesson {
  id: string;
  topic: string;
  created_at: string;
  rounds?: Round[];
}

interface LiveMessage {
  type: string;
  agent: string;
  block_id: string;
  content: string;
  reasoning: string;
  round: number;
  value_score?: number;
  override_score?: number;
  improvement_hint?: string;
}

interface LabsCategory {
  id: string;
  title: string;
  description: string;
}

interface LabsTool {
  id: string;
  name: string;
  category: string;
  criticality: string;
  status: string;
  summary: string;
  impact: string;
  phase: string;
}

interface LabsPhase {
  id: string;
  title: string;
  criticality: string;
  status: string;
  summary: string;
  deliverables: string[];
}

interface LabsLanguage {
  id: string;
  name: string;
  family: string;
  status: string;
}

interface AccessMode {
  id: string;
  name: string;
  summary: string;
  criticality: string;
}

interface CoworkSurface {
  id: string;
  name: string;
  status: string;
  inspiration: string;
  summary: string;
  features: string[];
}

interface OrchCodeTrack {
  id: string;
  title: string;
  priority: string;
  summary: string;
  topics: string[];
}

interface LabsOverview {
  title: string;
  positioning: string;
  categories: LabsCategory[];
  tools: LabsTool[];
  phases: LabsPhase[];
  languages: LabsLanguage[];
  access_modes: AccessMode[];
  cowork_surfaces: CoworkSurface[];
  orch_code_tracks: OrchCodeTrack[];
  metrics: {
    categories: number;
    tools: number;
    critical_tools: number;
    live_tools: number;
    languages: number;
    access_modes: number;
  };
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Lesson[]>([]);
  const [selectedSession, setSelectedSession] = useState<Lesson | null>(null);
  const [isAuditMode, setIsAuditMode] = useState(false);
  const [viewMode, setViewMode] = useState<'council' | 'labs'>('council');
  const [labsOverview, setLabsOverview] = useState<LabsOverview | null>(null);

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://127.0.0.1:8000/ws/live');

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'thinking') {
          setThinkingAgent(data.agent);
          setActiveAgent(null);
        } else if (data.type === 'response') {
          setThinkingAgent(null);
          setActiveAgent(data.agent);
          setMessages((prev) => [...prev, data]);
          setTimeout(() => setActiveAgent(null), 5000);
        } else if (data.type === 'override') {
          if (selectedSession && isAuditMode) {
            setSelectedSession((prev) => {
              if (!prev) return null;
              return {
                ...prev,
                rounds: prev.rounds?.map((r) => ({
                  ...r,
                  blocks: r.blocks.map((b) =>
                    b.block_id === data.block_id
                      ? {
                          ...b,
                          override_score: data.override_score,
                          improvement_hint: data.improvement_hint,
                        }
                      : b,
                  ),
                })),
              };
            });
          }
          setMessages((prev) =>
            prev.map((m) =>
              m.block_id === data.block_id
                ? {
                    ...m,
                    override_score: data.override_score,
                    improvement_hint: data.improvement_hint,
                  }
                : m,
            ),
          );
        }
      } catch (err) {
        console.error('Neural Link Error:', err);
      }
    };

    fetchSessions();
    fetchLabsOverview();
    return () => ws.current?.close();
  }, [selectedSession, isAuditMode]);

  const fetchSessions = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/sessions');
      const data = await resp.json();
      setSessions(data);
    } catch (err) {
      console.error('Vault Error:', err);
    }
  };

  const fetchLabsOverview = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/api/labs/overview');
      const data = await resp.json();
      setLabsOverview(data);
    } catch (err) {
      console.error('Labs Error:', err);
    }
  };

  const loadSession = async (id: string) => {
    try {
      setViewMode('council');
      setIsAuditMode(true);
      const resp = await fetch(`http://127.0.0.1:8000/sessions/${id}`);
      const data = await resp.json();
      setSelectedSession(data);
    } catch (err) {
      console.error('Audit Error:', err);
    }
  };

  const overrideScore = async (blockId: string, score: number) => {
    if (!selectedSession) return;
    try {
      await fetch(`http://127.0.0.1:8000/sessions/${selectedSession.id}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ block_id: blockId, override_score: score }),
      });
    } catch (err) {
      console.error('Override Error:', err);
    }
  };

  const openCouncil = () => {
    setViewMode('council');
    setIsAuditMode(false);
  };

  const openLabs = () => {
    setViewMode('labs');
    setIsAuditMode(false);
  };

  const agentList = ['orch', 'grok', 'gemini', 'claude', 'copilot'];
  const criticalityLabel = (value: string) => value.toUpperCase();

  return (
    <div className="command-center">
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">ORCH CONTROL</div>
        </div>
        <div className="lesson-list">
          <div className={`lesson-item ${viewMode === 'council' && !isAuditMode ? 'active' : ''}`} onClick={openCouncil}>
            <div className="lesson-topic">LIVE COUNCIL</div>
            <div className="lesson-date">Real-time apprenticeship</div>
          </div>
          <div className={`lesson-item ${viewMode === 'labs' ? 'active' : ''}`} onClick={openLabs}>
            <div className="lesson-topic">ORCH LABS</div>
            <div className="lesson-date">SA impact experiment studio</div>
          </div>
          <div className="sidebar-section-label">SESSION VAULT</div>
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`lesson-item ${selectedSession?.id === s.id && isAuditMode ? 'active' : ''}`}
              onClick={() => loadSession(s.id)}
            >
              <div className="lesson-topic">SESSION: {s.topic}</div>
              <div className="lesson-date">{new Date(s.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="main-room">
        {viewMode === 'labs' ? (
          <div className="labs-shell">
            <section className="labs-hero">
              <div className="labs-kicker">ORCH LABS</div>
              <h1>{labsOverview?.title ?? 'Orch Labs'}</h1>
              <p>{labsOverview?.positioning ?? 'A Google-Labs-style layer for South African public-impact AI tools.'}</p>
              <div className="labs-metrics">
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.tools ?? 0}</span>
                  <span className="metric-label">Tools</span>
                </div>
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.critical_tools ?? 0}</span>
                  <span className="metric-label">Critical</span>
                </div>
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.live_tools ?? 0}</span>
                  <span className="metric-label">Live</span>
                </div>
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.categories ?? 0}</span>
                  <span className="metric-label">Categories</span>
                </div>
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.languages ?? 0}</span>
                  <span className="metric-label">SA Languages</span>
                </div>
                <div className="metric-card">
                  <span className="metric-value">{labsOverview?.metrics.access_modes ?? 0}</span>
                  <span className="metric-label">Access Modes</span>
                </div>
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Categories</div>
              <div className="labs-grid categories-grid">
                {labsOverview?.categories.map((category) => (
                  <article key={category.id} className="labs-card category-card">
                    <div className="card-chip">{category.id.replace('-', ' ')}</div>
                    <h3>{category.title}</h3>
                    <p>{category.description}</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">South Africa Tool Catalog</div>
              <div className="labs-grid tools-grid">
                {labsOverview?.tools.map((tool) => (
                  <article key={tool.id} className="labs-card tool-card">
                    <div className="tool-card-top">
                      <div className="card-chip">{tool.phase}</div>
                      <div className={`criticality-pill ${tool.criticality}`}>{criticalityLabel(tool.criticality)}</div>
                    </div>
                    <h3>{tool.name}</h3>
                    <div className="tool-meta">{tool.category} · {tool.status}</div>
                    <p>{tool.summary}</p>
                    <div className="impact-label">Impact</div>
                    <div className="impact-copy">{tool.impact}</div>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Roadmap Phases</div>
              <div className="labs-grid phases-grid">
                {labsOverview?.phases.map((phase) => (
                  <article key={phase.id} className="labs-card phase-card">
                    <div className="tool-card-top">
                      <div className={`criticality-pill ${phase.criticality}`}>{criticalityLabel(phase.criticality)}</div>
                      <div className="card-chip">{phase.status.replace('_', ' ')}</div>
                    </div>
                    <h3>{phase.title}</h3>
                    <p>{phase.summary}</p>
                    <div className="deliverables-list">
                      {phase.deliverables.map((deliverable) => (
                        <div key={deliverable} className="deliverable-item">
                          {deliverable}
                        </div>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section split-section">
              <div className="split-panel">
                <div className="section-heading">SA Languages</div>
                <div className="labs-grid language-grid">
                  {labsOverview?.languages.map((language) => (
                    <article key={language.id} className="labs-card compact-card">
                      <div className="tool-card-top">
                        <h3>{language.name}</h3>
                        <div className="card-chip">{language.status.replace('_', ' ')}</div>
                      </div>
                      <p>{language.family}</p>
                    </article>
                  ))}
                </div>
              </div>
              <div className="split-panel">
                <div className="section-heading">Accessibility Modes</div>
                <div className="labs-grid access-grid">
                  {labsOverview?.access_modes.map((mode) => (
                    <article key={mode.id} className="labs-card compact-card">
                      <div className="tool-card-top">
                        <h3>{mode.name}</h3>
                        <div className={`criticality-pill ${mode.criticality}`}>{criticalityLabel(mode.criticality)}</div>
                      </div>
                      <p>{mode.summary}</p>
                    </article>
                  ))}
                </div>
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Cowork</div>
              <div className="labs-grid cowork-grid">
                {labsOverview?.cowork_surfaces.map((surface) => (
                  <article key={surface.id} className="labs-card phase-card">
                    <div className="tool-card-top">
                      <div className="card-chip">{surface.inspiration}</div>
                      <div className="card-chip">{surface.status}</div>
                    </div>
                    <h3>{surface.name}</h3>
                    <p>{surface.summary}</p>
                    <div className="deliverables-list">
                      {surface.features.map((feature) => (
                        <div key={feature} className="deliverable-item">
                          {feature}
                        </div>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="labs-section">
              <div className="section-heading">Orch Code</div>
              <div className="labs-grid phases-grid">
                {labsOverview?.orch_code_tracks.map((track) => (
                  <article key={track.id} className="labs-card phase-card">
                    <div className="tool-card-top">
                      <div className={`criticality-pill ${track.priority}`}>{criticalityLabel(track.priority)}</div>
                      <div className="card-chip">teach-first</div>
                    </div>
                    <h3>{track.title}</h3>
                    <p>{track.summary}</p>
                    <div className="deliverables-list">
                      {track.topics.map((topic) => (
                        <div key={topic} className="deliverable-item">
                          {topic}
                        </div>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        ) : !isAuditMode ? (
          agentList.map((id) => {
            const isStudent = id === 'orch';
            const isThinking = thinkingAgent === id;
            const isResponding = activeAgent === id;
            const lastMsg = messages.filter((m) => m.agent === id).slice(-1)[0];

            return (
              <div
                key={id}
                className={`chamber ${id} ${isThinking ? 'thinking' : ''} ${isResponding ? 'responding' : ''} ${isStudent ? 'student' : 'mentor'}`}
              >
                <div className="agent-rank">{isStudent ? '[STUDENT]' : '[MENTOR]'}</div>
                <div className="agent-id">{id}</div>
                {isThinking && <div className="glow-orb" />}
                <div className="response-text">
                  {isThinking ? (isStudent ? 'SYNTHESIZING DEEP REASONING...' : 'PROVIDING EXPERT ADVICE...') : lastMsg?.content || 'STANDBY...'}
                </div>
                {(lastMsg?.value_score !== undefined || lastMsg?.override_score !== undefined) && (
                  <div className="value-meter">
                    <div className="value-fill" style={{ width: `${(lastMsg.override_score ?? lastMsg.value_score ?? 0) * 10}%` }} />
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="audit-container">
            <div className="sidebar-title">Forensic Audit: {selectedSession?.topic}</div>
            {selectedSession?.rounds?.map((round) => (
              <div key={round.id} className="round-section">
                <div className="sidebar-title" style={{ fontSize: '0.7rem', color: 'var(--cyan-glow)', marginTop: '40px' }}>
                  ROUND {round.round_number} ANALYSIS
                </div>
                {round.blocks.map((block) => (
                  <div key={block.block_id} className={`audit-card ${block.is_student ? 'student' : 'mentor'}`}>
                    <div className="card-header">
                      <div className="card-agent">{block.agent.toUpperCase()}</div>
                      <div className="value-tag">MASTER SCORE: {block.override_score ?? block.value_score ?? 0}/10</div>
                    </div>
                    <div className="thought-body" style={{ color: 'white', marginBottom: '15px' }}>{block.content}</div>
                    <div className="thought-body">Reasoning Trace: {block.reasoning}</div>

                    <div className="override-container">
                      <input
                        type="range"
                        min="0"
                        max="10"
                        value={block.override_score ?? block.value_score ?? 0}
                        className="glow-knob"
                        aria-label="Master Override Logic Score"
                        onChange={(e) => overrideScore(block.block_id, parseInt(e.target.value, 10))}
                      />
                    </div>
                    {block.improvement_hint && <div className="improvement-hint">Master Hint: {block.improvement_hint}</div>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
