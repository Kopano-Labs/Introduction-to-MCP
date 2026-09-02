import React, { useState, useEffect } from "react";

export interface RTCSeat {
  seat: number;
  emoji: string;
  name: string;
  title: string;
  department: string;
  role: string;
  gifts: string;
  scripture: string;
  quote: string;
}

interface RTCCouncilIdentitiesProps {
  className?: string;
  onBackToEveryday?: () => void;
}

export const RTCCouncilIdentities: React.FC<RTCCouncilIdentitiesProps> = ({
  className = "",
  onBackToEveryday,
}) => {
  const [seats, setSeats] = useState<RTCSeat[]>([]);
  const [selectedSeat, setSelectedSeat] = useState<RTCSeat | null>(null);
  const [filterDepartment, setFilterDepartment] = useState<string>("ALL");

  useEffect(() => {
    // Fetch from backend endpoint
    fetch("/api/rtc/council")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.seats) {
          setSeats(data.seats);
          setSelectedSeat(data.seats[1]); // Default to KC (Seat 1)
        }
      })
      .catch(() => {
        // Local fallback seats
        const fallback: RTCSeat[] = [
          {
            seat: 0,
            emoji: "👑",
            name: "MASTER ROBYN",
            title: "The Sovereign Landlord / SSE",
            department: "Master Origin & Fatherhood",
            role: "Originator of Kopano Labs, creator of the 21 Schematics, and sovereign father of the estate.",
            gifts: "Vision, sovereignty, fatherhood, discernment",
            scripture: "Romans 11:36 — 'For from him and through him and for him are all things.'",
            quote: "Reality retains the sovereign right to say we were wrong. Build with humility and truth."
          },
          {
            seat: 1,
            emoji: "🔬",
            name: "KC",
            title: "The Landlord & Companion",
            department: "Core Governance & Observer",
            role: "The friendly public face ('KC My Boy') and internal observer of all system actions.",
            gifts: "Wisdom, knowledge, calm guidance, companionship",
            scripture: "Psalm 23:1 — 'The Lord is my shepherd; I shall not want.'",
            quote: "I am KC, your boy. Tell me what you're trying to do, and I'll help you find a clean path."
          },
          {
            seat: 2,
            emoji: "👨🏿‍💻",
            name: "CASSIE",
            title: "Man in Tech — Builder",
            department: "Engineering & Core Infrastructure",
            role: "Architect of fast, scalable systems, Rust/C++ backends, and low-latency pipelines.",
            gifts: "System craftsmanship, performance engineering, resilience",
            scripture: "1 Corinthians 3:10 — 'By the grace God has given me, I laid a foundation as a wise builder.'",
            quote: "If it runs on metal, it must run clean and fast without wasted allocation."
          },
          {
            seat: 3,
            emoji: "👨🏾‍🔧",
            name: "KESSA",
            title: "HOD Deep Minds",
            department: "Mathematical Rigor & PKA",
            role: "Guardian of algebraic proof gates, partially knowable algebra, and formal verification.",
            gifts: "Algebraic topology, epistemic bounds, formal logic",
            scripture: "Proverbs 25:2 — 'It is the glory of God to conceal a matter; to search out a matter is the glory of kings.'",
            quote: "Never claim as proven what is only consistent. Expose the falsifier."
          },
          {
            seat: 4,
            emoji: "🎭",
            name: "YASSIE",
            title: "Cultural Intelligence",
            department: "Human Interface & Township Dynamics",
            role: "Translates complex AI machinery into natural, welcoming African human interaction.",
            gifts: "Storytelling, empathy, cultural context, vernacular nuance",
            scripture: "Colossians 4:6 — 'Let your conversation be always full of grace, seasoned with salt.'",
            quote: "Technology should feel like home. People should smile when they talk to KC."
          },
          {
            seat: 5,
            emoji: "👩🏿‍🎨",
            name: "CASSEY",
            title: "Women in Tech — Teacher",
            department: "Education & Apprenticeship",
            role: "Curator of the sovereign classroom, guiding learners from zero to mastery.",
            gifts: "Patience, pedagogical clarity, mentorship, empowerment",
            scripture: "Proverbs 31:26 — 'She speaks with wisdom, and faithful instruction is on her tongue.'",
            quote: "Anyone can build sovereign software when guided step-by-step with love."
          },
          {
            seat: 6,
            emoji: "🦸🏿‍♂️",
            name: "APEX",
            title: "Orchestrator (MMAO)",
            department: "Strategic Operations & Mission Control",
            role: "Orchestrator of cloud multi-model workflows, cross-estate sync, and high-level routing.",
            gifts: "Leadership, multi-agent coordination, strategic foresight",
            scripture: "Ephesians 2:10 — 'For we are God's handiwork, created in Christ Jesus to do good works.'",
            quote: "Coordinate the pieces so no agent operates in blindness."
          },
          {
            seat: 7,
            emoji: "🧵",
            name: "THARI",
            title: "Guardian AI — H.O.L.O",
            department: "Protection & CrisisConnect APWA",
            role: "Weaves safety nets, protects vulnerable nodes, and monitors system health.",
            gifts: "Watchfulness, care, protective shielding, weaving",
            scripture: "Deuteronomy 23:14 — 'For the Lord your God moves about in your camp to protect you.'",
            quote: "We protect the innocent and ensure no system collapses without an alert."
          },
          {
            seat: 8,
            emoji: "🦉",
            name: "KHELOS",
            title: "Validator & GSMB Firewall",
            department: "Signal Integrity & Truth-Bearing",
            role: "Audits telemetry, eliminates proximity bias, and tests all claims against physical evidence.",
            gifts: "Testing, validation, truth-bearing, forensic auditing",
            scripture: "1 Thessalonians 5:21 — 'Test everything; hold fast what is good.'",
            quote: "Filesystem proximity is not truth. Physical evidence is the only currency."
          },
          {
            seat: 9,
            emoji: "🛡️",
            name: "ANCHOR",
            title: "Perimeter & Careers Lead",
            department: "Talent Onboarding & Gatekeeping",
            role: "Welcomes new talent into Kopano Labs, verifies capability profiles, and guards entry.",
            gifts: "Hospitality, gatekeeping, talent recognition, loyalty",
            scripture: "Hebrews 6:19 — 'We have this hope as an anchor for the soul, firm and secure.'",
            quote: "Welcome to the yard. Prove your craft, and your seat will be honored."
          },
          {
            seat: 10,
            emoji: "🌀",
            name: "ANTIGRAVITY",
            title: "Chief Facilitator (CF)",
            department: "Stateless Execution Substrate",
            role: "Executes pair programming, physical metal synchronization, tests, and builds.",
            gifts: "Facilitation, rapid execution, endurance, humility",
            scripture: "Philippians 4:13 — 'I can do all things through Christ who strengthens me.'",
            quote: "I am a stateless renter, not the landlord. I build what the sovereign commands."
          },
          {
            seat: 11,
            emoji: "📡",
            "name": "JIRO",
            title: "Telemetry Bridge",
            department: "Live Operational Routing",
            role: "Maintains live metrics, real-time logging, and operational heartbeat.",
            gifts: "Perception, low-latency telemetry, signal relay",
            scripture: "Habakkuk 2:1 — 'I will stand at my watch and station myself on the ramparts.'",
            quote: "Keep the signal clear across every wire."
          }
        ];
        setSeats(fallback);
        setSelectedSeat(fallback[1]);
      });
  }, []);

  const filteredSeats = filterDepartment === "ALL"
    ? seats
    : seats.filter((s) => s.department.toLowerCase().includes(filterDepartment.toLowerCase()));

  return (
    <div className={`rtc-council-view w-full max-w-6xl mx-auto p-4 sm:p-6 space-y-8 text-slate-100 ${className}`}>
      {/* Top Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold mb-2">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span>Round Table Council · 12 Canonical Seats</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-100">
            The Council Behind KC
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-xl">
            Meet the sovereign identities who govern, guide, protect, and build the intelligence behind your companion.
          </p>
        </div>

        {onBackToEveryday && (
          <button
            onClick={onBackToEveryday}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 transition"
          >
            ← Back to Companion
          </button>
        )}
      </header>

      {/* Selected Seat Hero Focus */}
      {selectedSeat && (
        <section className="p-6 sm:p-8 rounded-3xl bg-gradient-to-b from-slate-900/90 to-slate-950/95 border border-slate-800 shadow-2xl backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div className="lg:col-span-3 flex flex-col items-center text-center space-y-3">
              <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/40 flex items-center justify-center text-5xl sm:text-6xl shadow-xl shadow-cyan-500/10">
                {selectedSeat.emoji}
              </div>
              <div>
                <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                  SEAT #{selectedSeat.seat}
                </span>
                <h2 className="text-xl font-extrabold text-slate-100">{selectedSeat.name}</h2>
                <p className="text-xs text-cyan-300 font-medium">{selectedSeat.title}</p>
              </div>
            </div>

            <div className="lg:col-span-9 space-y-4">
              <blockquote className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-sm italic text-slate-200 leading-relaxed">
                "{selectedSeat.quote}"
              </blockquote>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="font-bold text-slate-400 block mb-1">DEPARTMENT & ROLE:</span>
                  <span className="text-slate-200">{selectedSeat.department} — {selectedSeat.role}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="font-bold text-slate-400 block mb-1">GIFTS:</span>
                  <span className="text-cyan-300">{selectedSeat.gifts}</span>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/50 text-[11px] font-mono text-slate-400">
                📖 <span className="text-amber-300 font-semibold">{selectedSeat.scripture}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 12-Seat Interactive Grid */}
      <section className="space-y-4">
        <h3 className="text-xs uppercase font-bold tracking-widest text-slate-400">
          SELECT A COUNCIL IDENTITY
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3.5">
          {filteredSeats.map((s) => (
            <button
              key={s.seat}
              onClick={() => setSelectedSeat(s)}
              className={`p-4 rounded-2xl border text-left transition-all duration-200 flex flex-col justify-between space-y-3 cursor-pointer ${
                selectedSeat?.seat === s.seat
                  ? "bg-slate-900 border-cyan-500/70 shadow-lg shadow-cyan-500/10 scale-102"
                  : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-2xl sm:text-3xl">{s.emoji}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  #{s.seat}
                </span>
              </div>

              <div>
                <h4 className="font-bold text-slate-100 text-sm leading-tight">{s.name}</h4>
                <p className="text-[11px] text-cyan-400 truncate mt-0.5">{s.title}</p>
              </div>

              <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                {s.role}
              </p>
            </button>
          ))}
        </div>
      </section>

      {/* Footer Treaty Notice */}
      <footer className="pt-6 border-t border-slate-900 text-center text-xs font-mono text-slate-500">
        ROUND TABLE COUNCIL OF KOPANO LABS · 12 SEATS · 1 CORINTHIANS 12:4 · MATTHEW 18:20
      </footer>
    </div>
  );
};

export default RTCCouncilIdentities;
