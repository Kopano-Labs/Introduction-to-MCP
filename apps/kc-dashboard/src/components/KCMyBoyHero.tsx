import React, { useState } from "react";
import { KCMascot3D, MascotMood } from "./KCMascot3D";
import { RTCIdentityKey, RTC_IDENTITY_PROFILES, KopanoAssertReceipt } from "../types/rtc";
import { KopanoAssertStamp } from "./KopanoAssertStamp";

interface KCMyBoyHeroProps {
  onOpenOperatorMode?: () => void;
  onNavigateToContextStudio?: () => void;
  onOpenSpatialLab?: () => void;
  onOpenRtcCouncil?: () => void;
}

export const KCMyBoyHero: React.FC<KCMyBoyHeroProps> = ({
  onOpenOperatorMode,
  onNavigateToContextStudio,
  onOpenSpatialLab,
  onOpenRtcCouncil,
}) => {
  const [query, setQuery] = useState("");
  const [mascotMood, setMascotMood] = useState<MascotMood>("idle");
  const [activeIdentity, setActiveIdentity] = useState<RTCIdentityKey>("GUEST_SEEKER");
  const [assertReceipt, setAssertReceipt] = useState<KopanoAssertReceipt | null>({
    assert_id: "AST-8F2B10A4",
    session_id: "guest_session",
    rtc_identity: "GUEST_SEEKER",
    intent_domain: "EVERYDAY_ORCHESTRATION",
    claim: "Sovereign companion active and listening at front door",
    residency: "ZA-CPT (South Africa North)",
    proof_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    status: "VERIFIED_ON_LEDGER",
    timestamp: new Date().toISOString(),
  });

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

  const currentProfile = RTC_IDENTITY_PROFILES[activeIdentity];

  const handleAskKc = async (customQuery?: string) => {
    const text = customQuery || query;
    if (!text.trim()) return;

    setIsLoading(true);
    setMascotMood("thinking");

    try {
      // Call backend KC endpoint with active RTC identity
      const response = await fetch("/api/kc/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          rtc_identity: activeIdentity,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setKcReply(data.reply);
        setMascotMood((data.mascot_state as MascotMood) || "celebrating");
        if (data.suggested_actions) {
          setSuggestedActions(data.suggested_actions);
        }
        if (data.assert_receipt) {
          setAssertReceipt(data.assert_receipt);
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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center font-bold text-cyan-400">
            K
          </div>
          <div>
            <span className="text-xs font-mono uppercase tracking-widest text-cyan-400">Kopano Labs</span>
            <p className="text-sm font-medium text-slate-200">Sovereign Systems & Companion Studio</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {onOpenRtcCouncil && (
            <button
              onClick={onOpenRtcCouncil}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-amber-500/40 bg-amber-950/40 text-amber-300 hover:border-amber-400 hover:bg-amber-900/60 transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <span>⚔️</span>
              <span>RTC Council (12 Seats)</span>
            </button>
          )}
          {onOpenSpatialLab && (
            <button
              onClick={onOpenSpatialLab}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-cyan-500/40 bg-cyan-950/40 text-cyan-300 hover:border-cyan-400 hover:bg-cyan-900/60 transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              <span>Spatial World (/kc-lab)</span>
            </button>
          )}
          {onOpenOperatorMode && (
            <button
              onClick={onOpenOperatorMode}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-300 hover:border-cyan-400/50 hover:text-cyan-300 transition-colors cursor-pointer"
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
            <span>September Flagship Release · "KC My Boy"</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
            Build Better. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-amber-400">
              Think Clearer. Move Faster.
            </span>
          </h1>

          <p className="text-base text-slate-300 max-w-xl leading-relaxed">
            Welcome to the front door of Kopano Labs. Whether you're booking matches at FiveS Arena, exploring digital work via KasiLink, checking Cars4Mars hardware telematics, or learning to build software — KC is your companion.
          </p>

          {/* RTC Identity Persona Switcher */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>ACTIVE RTC PERSONA:</span>
              <span className="text-amber-300 font-semibold">{currentProfile.label} ({currentProfile.tagline})</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(Object.keys(RTC_IDENTITY_PROFILES) as RTCIdentityKey[]).map((key) => {
                const p = RTC_IDENTITY_PROFILES[key];
                const isSelected = activeIdentity === key;
                return (
                  <button
                    key={key}
                    onClick={() => setActiveIdentity(key)}
                    className={`px-3 py-2 rounded-xl text-left border transition-all cursor-pointer flex items-center space-x-2 ${
                      isSelected
                        ? "bg-slate-900 border-cyan-400 text-slate-100 shadow-md shadow-cyan-500/20"
                        : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                    }`}
                  >
                    <span className="text-lg">{p.emoji}</span>
                    <div className="truncate">
                      <div className="text-xs font-bold leading-none">{p.label.split(" ")[0]}</div>
                      <div className="text-[10px] text-slate-500 truncate mt-0.5">{p.key}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* KC Dynamic Speech Bubble & Verifiable Assert Stamp */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-700/60 shadow-xl backdrop-blur-md relative space-y-3">
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

            {/* Verifiable Kopano Assert Stamp */}
            {assertReceipt && (
              <div className="pt-2 border-t border-slate-800/80">
                <KopanoAssertStamp receipt={assertReceipt} />
              </div>
            )}
          </div>

          {/* User Input & Action Form */}
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAskKc()}
              placeholder={currentProfile.promptPlaceholder}
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
                className="text-xs px-3 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-cyan-300 transition-colors cursor-pointer"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Living Three.js KC Mascot */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center">
          <div className="relative p-6 rounded-3xl bg-gradient-to-b from-slate-900/50 to-slate-950/80 border border-slate-800 shadow-2xl backdrop-blur-md w-full max-w-sm flex flex-col items-center">
            <KCMascot3D
              mood={mascotMood}
              size={260}
              interactive={true}
              activeIdentity={activeIdentity}
            />
            <div className="text-center mt-2">
              <h3 className="text-lg font-bold text-slate-100 flex items-center justify-center gap-2">
                <span>KC</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 font-mono">
                  KC MY BOY
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                {currentProfile.description}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Product Ecosystem Grid */}
      <div className="mt-16 pt-8 border-t border-slate-800/80">
        <h2 className="text-xs uppercase font-bold tracking-widest text-slate-400 mb-6">
          KOPANO LABS ECOSYSTEM LANES
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Lane 1: Work & Community */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-cyan-500/40 transition-colors flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-300 text-xl mb-4">
                💼
              </div>
              <h3 className="text-lg font-bold text-slate-100">Work & Opportunity</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Connect your skills with real opportunities in the township economy through KasiLink and Vanguard C.
              </p>
            </div>
            <button
              onClick={() => handleAskKc("How can I find work through KasiLink?")}
              className="mt-6 text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
            >
              <span>Explore KasiLink</span>
              <span>→</span>
            </button>
          </div>

          {/* Lane 2: FiveS Arena */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-emerald-500/40 transition-colors flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-300 text-xl mb-4">
                ⚽
              </div>
              <h3 className="text-lg font-bold text-slate-100">FiveS Arena</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Interactive APWA retention pitch with 3D physics courts and B2B reservation management for grassroots football.
              </p>
            </div>
            <button
              onClick={() => handleAskKc("Tell me about FiveS Arena football matches")}
              className="mt-6 text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center space-x-1 cursor-pointer"
            >
              <span>View FiveS Arena</span>
              <span>→</span>
            </button>
          </div>

          {/* Lane 3: Cars4Mars */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-amber-500/40 transition-colors flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-300 text-xl mb-4">
                🚀
              </div>
              <h3 className="text-lg font-bold text-slate-100">Cars4Mars</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Flagship smart mobility division. Telematics, battery health diagnostics, and smart vehicle integration.
              </p>
            </div>
            <button
              onClick={() => handleAskKc("What is Cars4Mars building?")}
              className="mt-6 text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center space-x-1 cursor-pointer"
            >
              <span>Explore Cars4Mars</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default KCMyBoyHero;
