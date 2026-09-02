import React, { useState } from "react";
import { KCMascot3D, MascotMood } from "./KCMascot3D";

interface KCMyBoyHeroProps {
  onOpenOperatorMode?: () => void;
  onNavigateToContextStudio?: () => void;
  onOpenSpatialLab?: () => void;
}

export const KCMyBoyHero: React.FC<KCMyBoyHeroProps> = ({
  onOpenOperatorMode,
  onNavigateToContextStudio,
  onOpenSpatialLab,
}) => {
  const [query, setQuery] = useState("");
  const [mascotMood, setMascotMood] = useState<MascotMood>("idle");
  const [kcReply, setKcReply] = useState<string>(
    "KC My Boy is ready! Ask me anything about your projects, township opportunities, or how Kopano Labs can help you build."
  );
  const [suggestedActions, setSuggestedActions] = useState<string[]>([
    "Explore KasiLink Work",
    "Cars4Mars Hardware",
    "Start Learning Code",
    "Organize Workspace"
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleAskKc = async (customQuery?: string) => {
    const text = customQuery || query;
    if (!text.trim()) return;

    setIsLoading(true);
    setMascotMood("thinking");

    try {
      // Call backend KC endpoint
      const response = await fetch("/api/kc/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (response.ok) {
        const data = await response.json();
        setKcReply(data.reply);
        setMascotMood(data.mascot_state as MascotMood || "celebrating");
        if (data.suggested_actions) {
          setSuggestedActions(data.suggested_actions);
        }
      } else {
        // Fallback local response
        setKcReply(`I'm with you, my boy! Let's get to work on: "${text}".`);
        setMascotMood("celebrating");
      }
    } catch {
      setKcReply(`I got you, my boy! Moving forward with: "${text}".`);
      setMascotMood("celebrating");
    } finally {
      setIsLoading(false);
      setQuery("");
      setTimeout(() => setMascotMood("idle"), 4000);
    }
  };

  return (
    <section className="kc-hero-container max-w-6xl mx-auto px-4 py-8 text-white">
      {/* Top Header Bar */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center font-bold text-cyan-400">
            K
          </div>
          <div>
            <h2 className="text-xs uppercase tracking-widest text-slate-400 font-semibold">KOPANO LABS</h2>
            <p className="text-sm font-medium text-slate-200">Sovereign Systems & Companion Studio</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {onOpenSpatialLab && (
            <button
              onClick={onOpenSpatialLab}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-cyan-500/40 bg-cyan-950/40 text-cyan-300 hover:border-cyan-400 hover:bg-cyan-900/60 transition-colors flex items-center gap-1.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              Spatial World (/kc-lab)
            </button>
          )}
          {onOpenOperatorMode && (
            <button
              onClick={onOpenOperatorMode}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-300 hover:border-cyan-400/50 hover:text-cyan-300 transition-colors"
            >
              Operator Control ↗
            </button>
          )}
        </div>
      </div>

      {/* Main Hero Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Column: Headline & Living Interaction */}
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>September Flagship Release</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
            Build Better. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-amber-400">
              Think Clearer. Move Faster.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-xl">
            Meet <strong className="text-cyan-300">KC</strong>, your Kopano companion. From ideas and projects to workflows and decisions, KC helps you move from chaos to clarity.
          </p>

          {/* KC Dynamic Speech Bubble */}
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/60 shadow-xl backdrop-blur-md relative">
            <div className="flex items-start space-x-3">
              <span className="text-xl">💬</span>
              <div className="flex-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-1">
                  KC My Boy says:
                </p>
                <p className="text-sm text-slate-200 font-medium leading-normal">
                  {kcReply}
                </p>
              </div>
            </div>
          </div>

          {/* User Input & Action Form */}
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAskKc()}
              placeholder="Tell KC what you're trying to do..."
              className="flex-1 px-4 py-3 rounded-xl bg-slate-950/80 border border-slate-700 focus:border-cyan-400 focus:outline-none text-slate-100 placeholder-slate-500 text-sm"
              disabled={isLoading}
            />
            <button
              onClick={() => handleAskKc()}
              disabled={isLoading}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 font-bold text-slate-950 text-sm shadow-lg shadow-cyan-500/20 transition-all cursor-pointer flex items-center justify-center space-x-2"
            >
              <span>{isLoading ? "Thinking..." : "Ask KC"}</span>
              <span>→</span>
            </button>
          </div>

          {/* Suggested Quick Chips */}
          <div className="flex flex-wrap gap-2 pt-1">
            <span className="text-xs text-slate-400 self-center mr-1">Try:</span>
            {suggestedActions.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleAskKc(chip)}
                className="text-xs px-3 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-cyan-300 transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Living Three.js KC Mascot */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center">
          <div className="relative p-6 rounded-3xl bg-gradient-to-b from-slate-900/50 to-slate-950/80 border border-slate-800 shadow-2xl backdrop-blur-md w-full max-w-sm flex flex-col items-center">
            <KCMascot3D mood={mascotMood} size={260} interactive={true} />
            <div className="text-center mt-2">
              <h3 className="text-lg font-bold text-slate-100 flex items-center justify-center gap-2">
                <span>KC</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 font-mono">
                  KC MY BOY
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Your Quiet Digital Guide</p>
            </div>
          </div>
        </div>
      </div>

      {/* Product Ecosystem Grid */}
      <div className="mt-16 pt-8 border-t border-slate-800/80">
        <h3 className="text-xs uppercase font-bold tracking-widest text-slate-400 mb-6 text-center sm:text-left">
          PRODUCTS & DIVISIONS POWERED BY KOPANO LABS
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            onClick={onNavigateToContextStudio}
            className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer group"
          >
            <div className="text-xl mb-2">⚡</div>
            <h4 className="font-bold text-slate-200 text-sm group-hover:text-cyan-400 transition-colors">
              Kopano Context Studio
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Human-AI collaboration that makes sense. Move from chaos to clarity.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-amber-500/40 transition-all cursor-pointer group">
            <div className="text-xl mb-2">🚗</div>
            <h4 className="font-bold text-slate-200 text-sm group-hover:text-amber-400 transition-colors">
              Cars4Mars
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Smart mobility & electric hardware division powered by Kopano Labs.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-emerald-500/40 transition-all cursor-pointer group">
            <div className="text-xl mb-2">🤝</div>
            <h4 className="font-bold text-slate-200 text-sm group-hover:text-emerald-400 transition-colors">
              KasiLink & Vanguard C
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Real work, township opportunity grids, and verified digital portfolios.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-indigo-500/40 transition-all cursor-pointer group">
            <div className="text-xl mb-2">⚽</div>
            <h4 className="font-bold text-slate-200 text-sm group-hover:text-indigo-400 transition-colors">
              FiveSArena
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Mobile-first 3D physics courts and hotel-grade match booking.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default KCMyBoyHero;
