import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  type: string;
  agent: string;
  content?: string;
  reasoning?: string;
  round: number;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 📡 NEURAL LINK CONNECTION
    ws.current = new WebSocket('ws://localhost:8000/ws/live');

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'thinking') {
          setThinkingAgent(data.agent);
          setActiveAgent(null);
        } else if (data.type === 'response') {
          setThinkingAgent(null);
          setActiveAgent(data.agent);
          
          // Add to data lake view
          setMessages((prev) => [...prev, data]);
          
          // Highlight temporary and move back to idle after 5s
          setTimeout(() => setActiveAgent(null), 5000);
        }
      } catch (err) {
        console.error("Neural Link Error:", err);
      }
    };

    return () => ws.current?.close();
  }, []);

  const agentList = ['grok', 'gemini', 'claude', 'copilot'];

  return (
    <div className="command-center">
      <div className="main-room">
        {agentList.map((id) => {
          const isThinking = thinkingAgent === id;
          const isResponding = activeAgent === id;
          const lastMsg = messages.filter(m => m.agent === id).slice(-1)[0];

          return (
            <div 
              key={id} 
              className={`chamber ${isThinking ? 'thinking' : ''} ${isResponding ? 'responding' : ''}`}
            >
              <div className="agent-id">{id}</div>
              {isThinking && <div className="glow-orb" />}
              <div className="response-text">
                {isThinking ? "PRODUCING REASONING CHAIN..." : lastMsg?.content || "STANDBY..."}
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="sidebar">
        <div className="sidebar-title">DEEP REASONING LAKE</div>
        <div className="thought-lake">
          {messages.map((m, i) => (
            <div key={i} className="thought-msg">
              <div className="thought-header">{m.agent.toUpperCase()} - ROUND {m.round}</div>
              <div className="thought-body">{m.reasoning}</div>
            </div>
          )).reverse()}
        </div>
      </div>
    </div>
  );
};

export default App;
