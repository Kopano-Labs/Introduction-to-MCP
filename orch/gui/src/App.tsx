import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  type: string;
  agent: string;
  block_id?: string;
  content?: string;
  reasoning?: string;
  round: number;
  value_score?: number;
  improvement_hint?: string;
}

interface Lesson {
  id: number;
  topic: string;
  created_at: string;
  agents: string[];
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Lesson[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [auditMessages, setAuditMessages] = useState<Message[]>([]);
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
          // Live sync of Master Overrides
          setMessages(prev => prev.map(m => 
            m.block_id === data.block_id 
              ? { ...m, value_score: data.value_score, improvement_hint: data.improvement_hint } 
              : m
          ));
          setAuditMessages(prev => prev.map(m => 
            m.block_id === data.block_id 
              ? { ...m, value_score: data.value_score, improvement_hint: data.improvement_hint } 
              : m
          ));
        }
      } catch (err) {
        console.error("Neural Link Error:", err);
      }
    };

    fetchSessions();
    return () => ws.current?.close();
  }, []);

  const fetchSessions = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/sessions');
      const data = await resp.json();
      setSessions(data);
    } catch (err) { console.error("Vault Error:", err); }
  };

  const loadSession = async (id: number) => {
    try {
      setSelectedSessionId(id);
      setIsAuditMode(true);
      const resp = await fetch(`http://127.0.0.1:8000/sessions/${id}`);
      const data = await resp.json();
      setAuditMessages(data.messages);
    } catch (err) { console.error("Audit Error:", err); }
  };

  const overrideScore = async (blockId: string, score: number, roundNum: number) => {
    if (!selectedSessionId) return;
    try {
      await fetch(`http://127.0.0.1:8000/sessions/${selectedSessionId}/round/${roundNum}/block/${blockId}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value_score: score })
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
              className={`lesson-item ${selectedSessionId === s.id && isAuditMode ? 'active' : ''}`}
              onClick={() => loadSession(s.id)}
            >
              <div className="lesson-topic">SESSION #{s.id}: {s.topic}</div>
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
                {lastMsg?.value_score !== undefined && (
                   <div className="value-meter"><div className="value-fill" style={{width: `${lastMsg.value_score * 10}%`}} /></div>
                )}
              </div>
            );
          })
        ) : (
          /* 🕵️ COGNITIVE AUDIT VIEW */
          <div className="audit-container">
            <div className="sidebar-title">Neural Audit Round-by-Round</div>
            {auditMessages.map((m, i) => (
              <div key={m.block_id || i} className={`audit-card ${m.agent === 'orch' ? 'student' : 'mentor'}`}>
                 <div className="card-header">
                    <div className="card-agent">{m.agent.toUpperCase()} - ROUND {m.round}</div>
                    <div className="value-tag">VALUATION: {m.value_score || 0}/10</div>
                 </div>
                 <div className="thought-body" style={{color: 'white', marginBottom: '15px'}}>{m.content}</div>
                 <div className="thought-body">🧠 Reasoning: {m.reasoning}</div>
                 
                 <div className="override-container">
                    <input 
                      type="range" min="0" max="10" 
                      value={m.value_score || 0} 
                      className="glow-knob"
                      aria-label="Master Override Logic Score"
                      onChange={(e) => overrideScore(m.block_id!, parseInt(e.target.value), m.round)}
                    />
                 </div>
                 {m.improvement_hint && <div className="improvement-hint">Master Input: {m.improvement_hint}</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
