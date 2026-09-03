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
  const [receipt, setReceipt] = useState<{
    assert_id: string;
    domain: string;
    proof: string;
    timestamp: string;
  } | null>({
    assert_id: "AST-7E2A91F0",
    domain: "KOPANO_SPATIAL_LAB",
    proof: "f8c2b740a3e81d769c02d184ebf5139029a1b65e89d0234cf78119ae90bc5231",
    timestamp: new Date().toLocaleTimeString(),
  });
  const [showForgeModal, setShowForgeModal] = useState(false);
  const [copied, setCopied] = useState(false);

  const domainDescriptions: Record<WorldDomain, { title: string; desc: string; system: string; color: string; bg: string }> = {
    general: {
      title: "Kopano Labs Space",
      desc: "KC is in equilibrium with the deformable context membrane. Move cursor to tilt, click to emit kinetic shockwaves.",
      system: "KC Motion Engine Core",
      color: "border-cyan-500 text-cyan-400",
      bg: "bg-cyan-950/40",
    },
    uyscuti: {
      title: "UY Scuti Forge Hypergiant Substrate",
      desc: "Multi-model reasoning convergence field linking Forge, AG, and the Round Table Council into a stellar accretion membrane.",
      system: "Hypergiant Multi-Model Engine",
      color: "border-rose-500 text-rose-400",
      bg: "bg-rose-950/40",
    },
    work: {
      title: "KasiLink & Vanguard C Opportunity Grid",
      desc: "Deploys sovereign township work nodes, digital freelance contracts, and capability verification bridges.",
      system: "Township Economic Engine",
      color: "border-amber-500 text-amber-400",
      bg: "bg-amber-950/40",
    },
    football: {
      title: "FiveS Arena Retention Space",
      desc: "3D kinetic pitch geometry, physics-based ball mechanics, and real-time Cape Town match reservations.",
      system: "APWA Kinetic Arena",
      color: "border-emerald-500 text-emerald-400",
      bg: "bg-emerald-950/40",
    },
    cars4mars: {
      title: "Cars4Mars DFR-01 Heavy Engineering",
      desc: "Telematics hex-lattice, 6-wheel skid-steer motor telemetry, and South African rover hardware diagnostics.",
      system: "Heavy Hardware & Mobility",
      color: "border-orange-500 text-orange-400",
      bg: "bg-orange-950/40",
    },
    learning: {
      title: "Sovereign Apprenticeship Monoliths",
      desc: "Step-by-step modular software mastery from zero to sovereign engineering without confusing tech jargon.",
      system: "Classroom / Cassey Engine",
      color: "border-purple-500 text-purple-400",
      bg: "bg-purple-950/40",
    },
  };

  const handleMascotClick = () => {
    setMood("celebrating");
    const rand = Math.floor(100000 + Math.random() * 900000);
    const mockHash = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
    setReceipt({
      assert_id: `AST-${rand.toString(16).toUpperCase()}`,
      domain: domain.toUpperCase(),
      proof: mockHash,
      timestamp: new Date().toLocaleTimeString(),
    });
    setTimeout(() => setMood("idle"), 2500);
  };

  const handleCopyProof = () => {
    if (receipt) {
      navigator.clipboard.writeText(receipt.proof);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 flex flex-col items-center justify-between space-y-6">
      {/* Top Bar Navigation */}
      <header className="w-full max-w-6xl flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToEveryday}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
          >
            ← Back to Everyday
          </button>
          <span className="text-sm font-bold tracking-wide text-cyan-400">
            KOPANO LABS · KC SPATIAL LAB (/kc-lab)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowForgeModal(true)}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 border border-rose-500/40 transition cursor-pointer flex items-center gap-1.5"
          >
            <span>🌌</span>
            <span>UY Scuti Receipt</span>
          </button>
          <button
            onClick={onOpenOperatorMode}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition cursor-pointer"
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
        <div className="w-full grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {(["general", "uyscuti", "work", "football", "cars4mars", "learning"] as WorldDomain[]).map((d) => (
            <button
              key={d}
              onClick={() => {
                setDomain(d);
                setMood("thinking");
                setTimeout(() => setMood("idle"), 1200);
              }}
              className={`px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                domain === d
                  ? `${domainDescriptions[d].color} ${domainDescriptions[d].bg} shadow-lg scale-102`
                  : "border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {d === "uyscuti" ? "UY SCUTI" : d.toUpperCase()}
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
            <div className="px-3.5 py-2.5 rounded-xl bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 text-xs font-mono flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="font-bold text-amber-300">{receipt.assert_id}</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-300">Verified ZA-CPT</span>
              </div>
              <button
                onClick={handleCopyProof}
                className="text-[10px] px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition cursor-pointer"
              >
                {copied ? "✓ Copied" : "Copy Proof"}
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Forge UY Scuti Visual Assertion Modal */}
      {showForgeModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-rose-500/40 rounded-3xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <span className="text-xl">🌌</span>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">
                    UY Scuti — Forge × AG × RTC Visual Assertion
                  </h3>
                  <p className="text-[11px] font-mono text-rose-400">
                    STATUS: VISUAL_ASSERTION_POC_0 · GOVERNED RECEIPT
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowForgeModal(false)}
                className="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs cursor-pointer"
              >
                ✕ Close
              </button>
            </div>

            <div className="rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 max-h-64 flex items-center justify-center">
              <img
                src="/assets/branding/sep-26/assets/UY_SCUTI_FORGE_X_AG_X_RTC_VISUAL_ASSERTION_POC_0.jpg"
                alt="UY Scuti Forge Visual Assertion"
                className="w-full h-auto object-cover"
              />
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-2 text-slate-300">
              <p className="font-semibold text-rose-300">
                Epistemic Boundary Discipline:
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                This asset is preserved as a visual assertion of multi-model alignment (KC front door, RTC capability depth, obsidian/cyan/gold palette). Per Forge's receipt, generated labels, mock statuses, and synthetic timestamps are explicitly non-authoritative.
              </p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setShowForgeModal(false)}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs cursor-pointer"
              >
                Acknowledge & Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer Sovereign Law */}
      <footer className="w-full max-w-6xl text-center text-[11px] font-mono text-slate-500 pt-4 border-t border-slate-900">
        KOPANO LABS SPATIAL PROVING GROUND · SECOND-ORDER SPRING KINEMATICS · UY SCUTI STELLAR ACCRETION
      </footer>
    </div>
  );
};

export default KCSpatialLab;
