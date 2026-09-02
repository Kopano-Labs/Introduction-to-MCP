import React, { useState } from "react";
import { KCSpatialWorld, WorldDomain, MascotMood } from "./KCSpatialWorld";

interface KCSpatialLabProps {
  onBackToEveryday: () => void;
  onOpenOperatorMode: () => void;
}

export const KCSpatialLab: React.FC<KCSpatialLabProps> = ({
  onBackToEveryday,
  onOpenOperatorMode,
}) => {
  const [domain, setDomain] = useState<WorldDomain>("general");
  const [mood, setMood] = useState<MascotMood>("idle");
  const [receipt, setReceipt] = useState<string | null>(null);

  const domainDescriptions: Record<WorldDomain, { title: string; desc: string; system: string; color: string }> = {
    general: {
      title: "Kopano Labs Space",
      desc: "KC is in equilibrium with the deformable context membrane. Move cursor to tilt, click to emit kinetic shockwaves.",
      system: "KC Motion Engine Core",
      color: "border-cyan-500 text-cyan-400",
    },
    work: {
      title: "KasiLink & Vanguard C Opportunity Grid",
      desc: "Deploys sovereign township work nodes, digital freelance contracts, and capability verification bridges.",
      system: "Township Economic Engine",
      color: "border-amber-500 text-amber-400",
    },
    football: {
      title: "FiveS Arena Retention Space",
      desc: "3D kinetic pitch geometry, physics-based ball mechanics, and real-time Cape Town match reservations.",
      system: "APWA Kinetic Arena",
      color: "border-emerald-500 text-emerald-400",
    },
    cars4mars: {
      title: "Cars4Mars DFR-01 Heavy Engineering",
      desc: "Telematics hex-lattice, 6-wheel skid-steer motor telemetry, and South African rover hardware diagnostics.",
      system: "Heavy Hardware & Mobility",
      color: "border-orange-500 text-orange-400",
    },
    learning: {
      title: "Sovereign Apprenticeship Monoliths",
      desc: "Step-by-step modular software mastery from zero to sovereign engineering without confusing tech jargon.",
      system: "Classroom / Cassey Engine",
      color: "border-purple-500 text-purple-400",
    },
  };

  const handleMascotClick = () => {
    setMood("celebrating");
    setReceipt(`RECEIPT #${Math.floor(100000 + Math.random() * 900000)} · Verified by KC · Time: ${new Date().toLocaleTimeString()} · Data Residency: SA North`);
    setTimeout(() => setMood("idle"), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 flex flex-col items-center justify-between space-y-6">
      {/* Top Bar Navigation */}
      <header className="w-full max-w-6xl flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToEveryday}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            ← Back to Everyday
          </button>
          <span className="text-sm font-bold tracking-wide text-cyan-400">
            KOPANO LABS · KC SPATIAL LAB (/kc-lab)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenOperatorMode}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition"
          >
            Operator View
          </button>
        </div>
      </header>

      {/* Spatial Canvas Container */}
      <main className="w-full max-w-6xl flex flex-col items-center space-y-6">
        <div className="w-full relative shadow-2xl rounded-3xl border border-slate-800 bg-slate-950 overflow-hidden">
          <KCSpatialWorld
            domain={domain}
            mood={mood}
            onMascotClick={handleMascotClick}
            className="w-full"
          />
        </div>

        {/* Domain Control Deck */}
        <div className="w-full grid grid-cols-2 sm:grid-cols-5 gap-2.5">
          {(["general", "work", "football", "cars4mars", "learning"] as WorldDomain[]).map((d) => (
            <button
              key={d}
              onClick={() => {
                setDomain(d);
                setMood("thinking");
                setTimeout(() => setMood("idle"), 1200);
              }}
              className={`px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all border ${
                domain === d
                  ? `${domainDescriptions[d].color} bg-slate-900 shadow-lg scale-102`
                  : "border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {d.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Dynamic Domain Briefing & Receipt Card */}
        <div className="w-full p-5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-slate-400">ACTIVE FORMATION:</span>
              <span className={`text-sm font-bold ${domainDescriptions[domain].color.split(" ")[1]}`}>
                {domainDescriptions[domain].title}
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">
              {domainDescriptions[domain].desc}
            </p>
          </div>

          {receipt && (
            <div className="px-3.5 py-2 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 text-xs font-mono animate-fade-in flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span>{receipt}</span>
            </div>
          )}
        </div>
      </main>

      {/* Footer Sovereign Law */}
      <footer className="w-full max-w-6xl text-center text-[11px] font-mono text-slate-500 pt-4 border-t border-slate-900">
        KOPANO LABS SPATIAL PROVING GROUND · SECOND-ORDER SPRING KINEMATICS · ADAPTIVE MULTI-TIER
      </footer>
    </div>
  );
};

export default KCSpatialLab;
