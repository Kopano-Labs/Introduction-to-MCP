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

const App: React.FC = () => {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Lesson[]>([]);
  const [selectedSession, setSelectedSession] = useState<Lesson | null>(null);
  const [isAuditMode, setIsAuditMode] = useState(false);
  
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 📡 NEURAL LINK CONNECTION
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
          // Live sync of Master Overrides in relational tree
          if (selectedSession && isAuditMode) {
            setSelectedSession(prev => {
              if (!prev) return null;
              return {
                ...prev,
                rounds: prev.rounds?.map(r => ({
                  ...r,
                  blocks: r.blocks.map(b => b.block_id === data.block_id 
                    ? { ...b, override_score: data.override_score, improvement_hint: data.improvement_hint } 
                    : b
                  )
                }))
              };
            });
          }
          // Also sync live view messages
          setMessages(prev => prev.map(m => m.block_id === data.block_id 
            ? { ...m, override_score: data.override_score, improvement_hint: data.improvement_hint } 
            : m
          ));
        }
      } catch (err) {
        console.error("Neural Link Error:", err);
      }
    };

    fetchSessions();
    return () => ws.current?.close();
  }, [selectedSession, isAuditMode]);

  const fetchSessions = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/sessions');
      const data = await resp.json();
      setSessions(data);
    } catch (err) { console.error("Vault Error:", err); }
  };

  const loadSession = async (id: string) => {
    try {
      setIsAuditMode(true);
      const resp = await fetch(`http://127.0.0.1:8000/sessions/${id}`);
      const data = await resp.json();
      setSelectedSession(data);
    } catch (err) { console.error("Audit Error:", err); }
  };

  const overrideScore = async (blockId: string, score: number) => {
    if (!selectedSession) return;
    try {
      await fetch(`http://127.0.0.1:8000/sessions/${selectedSession.id}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ block_id: blockId, override_score: score })
      });
    } catch (err) { console.error("Override Error:", err); }
  };

  const agentList = ['orch', 'grok', 'gemini', 'claude', 'copilot'];

  return (
    <div className="command-center">
      {/* 🏺 LESSON VAULT SIDEBAR */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">LESSON VAULT</div>
        </div>
        <div className="lesson-list">
          <div className={`lesson-item ${!isAuditMode ? 'active' : ''}`} onClick={() => setIsAuditMode(false)}>
            <div className="lesson-topic">🚀 LIVE COUNCIL</div>
            <div className="lesson-date">Real-time Apprenticeship</div>
          </div>
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
        {!isAuditMode ? (
          /* 🏛️ LIVE COUNCIL ROOM */
          agentList.map((id) => {
            const isStudent = id === 'orch';
            const isThinking = thinkingAgent === id;
            const isResponding = activeAgent === id;
            const lastMsg = messages.filter(m => m.agent === id).slice(-1)[0];

            return (
              <div 
                key={id} 
                className={`chamber ${id} ${isThinking ? 'thinking' : ''} ${isResponding ? 'responding' : ''} ${isStudent ? 'student' : 'mentor'}`}
              >
                <div className="agent-rank">{isStudent ? "[STUDENT]" : "[MENTOR]"}</div>
                <div className="agent-id">{id}</div>
                {isThinking && <div className="glow-orb" />}
                <div className="response-text">
                  {isThinking ? (isStudent ? "SYNTHESIZING DEEP REASONING..." : "PROVIDING EXPERT ADVICE...") : lastMsg?.content || "STANDBY..."}
                </div>
                {(lastMsg?.value_score !== undefined || lastMsg?.override_score !== undefined) && (
                   <div className="value-meter">
                     <div className="value-fill" style={{width: `${(lastMsg.override_score ?? lastMsg.value_score ?? 0) * 10}%`}} />
                   </div>
                )}
              </div>
            );
          })
        ) : (
          /* 🕵️ COGNITIVE AUDIT VIEW (Hierarchical) */
          <div className="audit-container">
            <div className="sidebar-title">Forensic Audit: {selectedSession?.topic}</div>
            {selectedSession?.rounds?.map((round) => (
              <div key={round.id} className="round-section">
                <div className="sidebar-title" style={{fontSize: '0.7rem', color: 'var(--cyan-glow)', marginTop: '40px'}}>
                   ROUND {round.round_number} ANALYSIS
                </div>
                {round.blocks.map((block) => (
                  <div key={block.block_id} className={`audit-card ${block.is_student ? 'student' : 'mentor'}`}>
                    <div className="card-header">
                      <div className="card-agent">{block.agent.toUpperCase()} </div>
                      <div className="value-tag">MASTER SCORE: {block.override_score ?? block.value_score ?? 0}/10</div>
                    </div>
                    <div className="thought-body" style={{color: 'white', marginBottom: '15px'}}>{block.content}</div>
                    <div className="thought-body">🧠 Reasoning Trace: {block.reasoning}</div>
                    
                    <div className="override-container">
                      <input 
                        type="range" min="0" max="10" 
                        value={block.override_score ?? block.value_score ?? 0} 
                        className="glow-knob"
                        aria-label="Master Override Logic Score"
                        onChange={(e) => overrideScore(block.block_id, parseInt(e.target.value))}
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
