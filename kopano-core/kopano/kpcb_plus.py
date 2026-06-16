"""
KPCB+ (Kopano-Phu Code Blocks Plus) — Runtime Compiler
========================================================
The coding language that communicates with ALL coding languages through protocols.

KPCB+ operates EXCLUSIVELY inside AI context windows.
It is not compiled on a machine — it is compiled IN the conversation.

7 Protocol Channels:
    PP  (Prompting Protocols)  — The voice
    BP  (Bracket Protocols)    — The structure
    EP  (Emoji Protocols)      — The identity
    GP  (GIF Protocols)        — The motion
    SP  (Sticker Protocols)    — The stamp
    .P  (MP4 Protocols)        — The evidence
    IP  (Image Protocols)      — The blueprint

Activation: FSM -> FSMP -> KPCB+ compiler
Guardian:   THARI GAI (navigates users)
Validator:  KC Ledger (4Ws gate)
Filter:     IIDP (FOC removal)

"LPHs are lazy. LPMs are lazy. That is POC of FOC.
 KPCB+ uses laziness AS A FEATURE — the governed path IS the shortcut."
"""

import json
import os
import re
from datetime import datetime, timezone


# ══════════════════════════════════════════════════════════════
# KPCB+ Protocol Channels
# ══════════════════════════════════════════════════════════════

PROTOCOL_CHANNELS = {
    "PP": {
        "emoji": "\U0001F4AC",  # 💬
        "name": "Prompting Protocols",
        "role": "voice",
        "description": "Natural language instructions structured as protocols",
    },
    "BP": {
        "emoji": "\u2604\uFE0F",  # ☄️
        "name": "Bracket Protocols",
        "role": "structure",
        "brackets": {"[]": "hierarchy", "{}": "keynote", "<>": "ark_story", "()": "understanding"},
    },
    "EP": {
        "emoji": "\U0001F976",  # 🥶
        "name": "Emoji Protocols",
        "role": "identity",
        "description": "Visual token encoding for MXIT-native communication",
    },
    "GP": {
        "emoji": "\U0001F3AC",  # 🎬
        "name": "GIF Protocols",
        "role": "motion",
        "description": "Animated micro-instructions for visual learners",
    },
    "SP": {
        "emoji": "\U0001F3F7\uFE0F",  # 🏷️
        "name": "Sticker Protocols",
        "role": "stamp",
        "description": "Governance seals, approval markers, status badges",
    },
    "dotP": {
        "emoji": "\U0001F3A5",  # 🎥
        "name": ".MP4 Protocols",
        "role": "evidence",
        "description": "Video proof of LPH validation",
    },
    "IP": {
        "emoji": "\U0001F5BC\uFE0F",  # 🖼️
        "name": "Image Protocols",
        "role": "blueprint",
        "description": "Diagrams and architecture visuals as code context",
    },
}

# Target languages KPCB+ can emit
TARGET_LANGUAGES = [
    "python", "javascript", "typescript", "rust", "go", "csharp", "java",
    "html", "css", "sql", "bash", "powershell", "webgl", "glsl",
    "markdown", "json", "yaml", "toml",
]

# Emoji entity index for EP channel
EMOJI_ENTITIES = {
    "\U0001F52C": "KC",            # 🔬
    "\U0001F6BA": "Female",        # 🚺
    "\U0001F6B9": "Male",          # 🚹
    "\U0001F6B6": "Person",        # 🚶
    "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466": "Family",  # 👨‍👩‍👧‍👦
    "\U0001F980": "Crab",          # 🦀
    "\u264A": "Gemini",            # ♊
    "\U0001F624": "Frustrated",    # 😤
    "\U0001F479": "Ogre",          # 👹
    "\U0001F426\u200D\U0001F525": "Phoenix",  # 🐦‍🔥
    "\U0001F4AC": "MXIT",          # 💬
    "\U0001F9B8\U0001F3FF\u200D\u2642\uFE0F": "MMAO",  # 🦸🏿‍♂️
    "\U0001F393": "KPGS",          # 🎓
    "\U0001F977\U0001F3FF": "KPSMB",  # 🥷🏿
    "\u2692\uFE0F": "KasiLink",    # ⚒️
    "\U0001F5FF": "CapeCompass",   # 🗿
    "\U0001F4BC": "AmaPhu",        # 💼
    "\U0001F680": "KopanoLabs",    # 🚀
    "\u26BD": "FivesArena",        # ⚽
    "\U0001F6A8": "CrisisConnect", # 🚨
    "\U0001F3C1": "StarfallSalvage", # 🏁
}


# ══════════════════════════════════════════════════════════════
# KPCB+ Code Block Parser
# ══════════════════════════════════════════════════════════════

class KPCBBlock:
    """A single KPCB+ code block — the fundamental unit of the language."""

    def __init__(self, raw_text):
        self.raw = raw_text
        self.hierarchy = None      # [ ]
        self.keynote = None        # { }
        self.ark_story = None      # < >
        self.understanding = None  # ( )
        self.pp_lines = []         # 💬PP: lines
        self.bp_lines = []         # ☄️BP: lines
        self.ep_lines = []         # 🥶EP: lines
        self.gp_lines = []         # 🎬GP: lines
        self.sp_lines = []         # 🏷️SP: lines
        self.dotp_lines = []       # 🎥.P: lines
        self.ip_lines = []         # 🖼️IP: lines
        self.target_language = None
        self.pso_level = None
        self.seal = False
        self.four_ws = {}
        self.errors = []
        self._parse()

    def _parse(self):
        """Parse the raw KPCB+ block into protocol channels."""
        lines = self.raw.strip().split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Bracket protocol parsing
            h_match = re.match(r'^\[(.+?)\]\s*\{(.+?)\}', stripped)
            if h_match:
                self.hierarchy = h_match.group(1).strip()
                self.keynote = h_match.group(2).strip()
                continue

            ark_match = re.match(r'^<(.+?)>', stripped)
            if ark_match and not stripped.startswith("< "):
                self.ark_story = ark_match.group(1).strip()
                continue

            und_match = re.match(r'^\((.+?)\)', stripped)
            if und_match:
                self.understanding = und_match.group(1).strip()
                continue

            # Protocol channel lines
            if "PP:" in stripped:
                self.pp_lines.append(stripped.split("PP:", 1)[1].strip())
            elif "BP:" in stripped:
                self.bp_lines.append(stripped.split("BP:", 1)[1].strip())
            elif "EP:" in stripped:
                self.ep_lines.append(stripped.split("EP:", 1)[1].strip())
            elif "GP:" in stripped:
                self.gp_lines.append(stripped.split("GP:", 1)[1].strip())
            elif "SP:" in stripped:
                self.sp_lines.append(stripped.split("SP:", 1)[1].strip())
            elif ".P:" in stripped:
                self.dotp_lines.append(stripped.split(".P:", 1)[1].strip())
            elif "IP:" in stripped:
                self.ip_lines.append(stripped.split("IP:", 1)[1].strip())

            # Target language
            if stripped.startswith("TARGET:") or "TARGET:" in stripped:
                target = stripped.split("TARGET:", 1)[1].strip().lower()
                for lang in TARGET_LANGUAGES:
                    if lang in target:
                        self.target_language = lang
                        break

            # PSO level
            if "PSO:" in stripped:
                pso_raw = stripped.split("PSO:", 1)[1].strip().upper()
                for level in ["SPSO", "BPSO", "GPSO", "LPSO"]:
                    if level in pso_raw:
                        self.pso_level = level
                        break

            # SEAL
            if "SEAL:" in stripped:
                self.seal = True

            # 4Ws
            if "4Ws:" in stripped or "4WS:" in stripped:
                ws_raw = stripped.split(":", 1)[1].strip()
                for pair in ws_raw.split("|"):
                    if "=" in pair:
                        k, v = pair.strip().split("=", 1)
                        self.four_ws[k.strip().upper()] = v.strip()

    def validate(self):
        """KC Ledger 4Ws validation — POC or FOC determination."""
        result = {
            "block": self.hierarchy or "UNNAMED",
            "channels_active": 0,
            "channels": [],
            "target_language": self.target_language,
            "pso_level": self.pso_level,
            "sealed": self.seal,
            "four_ws": self.four_ws,
            "errors": [],
            "verdict": "UNKNOWN",
        }

        # Count active channels
        channel_checks = [
            ("PP", len(self.pp_lines) > 0),
            ("BP", len(self.bp_lines) > 0 or self.hierarchy is not None),
            ("EP", len(self.ep_lines) > 0),
            ("GP", len(self.gp_lines) > 0),
            ("SP", len(self.sp_lines) > 0),
            ("dotP", len(self.dotp_lines) > 0),
            ("IP", len(self.ip_lines) > 0),
        ]
        for name, active in channel_checks:
            if active:
                result["channels_active"] += 1
                result["channels"].append(name)

        # Minimum requirements: PP + BP must be present
        if "PP" not in result["channels"]:
            result["errors"].append("MISSING PP (Prompting Protocol) — voice is required")
        if "BP" not in result["channels"]:
            result["errors"].append("MISSING BP (Bracket Protocol) — structure is required")

        # 4Ws validation
        required_ws = ["WHO", "WHAT", "WHERE", "WHY"]
        missing_ws = [w for w in required_ws if w not in self.four_ws]
        if missing_ws:
            result["errors"].append("MISSING 4Ws: " + ", ".join(missing_ws))

        # Verdict
        if len(result["errors"]) == 0:
            result["verdict"] = "POC_VALIDATED"
        elif len(result["errors"]) <= 2:
            result["verdict"] = "PARTIAL_POC"
        else:
            result["verdict"] = "FOC_DETECTED"

        return result

    def to_dict(self):
        return {
            "hierarchy": self.hierarchy,
            "keynote": self.keynote,
            "ark_story": self.ark_story,
            "understanding": self.understanding,
            "pp": self.pp_lines,
            "bp": self.bp_lines,
            "ep": self.ep_lines,
            "gp": self.gp_lines,
            "sp": self.sp_lines,
            "dotp": self.dotp_lines,
            "ip": self.ip_lines,
            "target": self.target_language,
            "pso": self.pso_level,
            "sealed": self.seal,
            "four_ws": self.four_ws,
        }


# ══════════════════════════════════════════════════════════════
# KPCB+ Compiler
# ══════════════════════════════════════════════════════════════

class KPCBPlusCompiler:
    """
    KPCB+ Compiler — compiles Kopano-Phu Code Blocks into target language output.

    This compiler operates INSIDE the AI context window.
    It does not generate machine code — it generates governed, validated,
    protocol-mediated code in the target language.

    FSM -> FSMP -> KPCB+ compiler activates.
    THARI GAI navigates. KC Ledger validates. IIDP filters.
    """

    def __init__(self):
        self.channels = PROTOCOL_CHANNELS
        self.targets = TARGET_LANGUAGES
        self.entities = EMOJI_ENTITIES
        self.blocks_compiled = []
        self.compilation_log = []

    def compile_block(self, raw_kpcb):
        """
        Compile a KPCB+ code block.

        Flow:
        1. Parse raw text into KPCBBlock
        2. FSMP activation — forensic validation
        3. THARI GAI — navigate protocol channels
        4. KC Ledger — 4Ws validation
        5. IIDP filter — remove FOC
        6. Emit target language code
        7. SWFUS Seal
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Step 1: Parse
        block = KPCBBlock(raw_kpcb)

        # Step 2: FSMP activation
        fsmp_result = self._fsmp_activate(block)

        # Step 3: THARI GAI navigation
        gai_result = self._thari_gai_navigate(block)

        # Step 4: KC Ledger 4Ws validation
        validation = block.validate()

        # Step 5: IIDP filter
        iidp_result = self._iidp_filter(block)

        # Step 6: Determine target
        target = block.target_language or "python"

        # Compile entry
        entry = {
            "ts": ts,
            "compiler": "KPCB+",
            "block_name": block.hierarchy or "UNNAMED",
            "channels_active": validation["channels_active"],
            "channels": validation["channels"],
            "target_language": target,
            "pso_level": block.pso_level or "GPSO",
            "sealed": block.seal,
            "four_ws": block.four_ws,
            "fsmp": fsmp_result,
            "gai": gai_result,
            "iidp": iidp_result,
            "validation": validation["verdict"],
            "errors": validation["errors"],
        }

        self.blocks_compiled.append(entry)
        self.compilation_log.append(entry)
        return entry

    def _fsmp_activate(self, block):
        """FSM -> FSMP activation. Forensic Sociology validates the intent."""
        forensic_signals = []

        # Check for lazy patterns (POC of FOC — use to advantage)
        if block.pp_lines:
            for line in block.pp_lines:
                lower = line.lower()
                if any(w in lower for w in ["copy", "paste", "hack", "shortcut"]):
                    forensic_signals.append("LAZY_PATTERN_DETECTED")
                if any(w in lower for w in ["generate", "create", "build", "deploy"]):
                    forensic_signals.append("CONSTRUCTIVE_INTENT")

        return {
            "activated": True,
            "mode": "FORENSIC_SOCIOLOGY",
            "signals": forensic_signals if forensic_signals else ["NEUTRAL"],
            "verdict": "PROCEED",
        }

    def _thari_gai_navigate(self, block):
        """THARI GAI layer — help user navigate KPCB+ compilation."""
        recommendations = []

        if not block.pp_lines:
            recommendations.append("Add PP (Prompting Protocol) — express your intent")
        if not block.hierarchy:
            recommendations.append("Add [ ] bracket — define the hierarchy")
        if not block.keynote:
            recommendations.append("Add { } bracket — state the keynote thesis")
        if not block.ep_lines:
            recommendations.append("Add EP (Emoji Protocol) — tag with semantic emojis")
        if not block.target_language:
            recommendations.append("Specify TARGET language for code emission")
        if not block.four_ws:
            recommendations.append("Add 4Ws (WHO/WHAT/WHERE/WHY) for KC Ledger validation")

        return {
            "guardian": "THARI",
            "recommendations": recommendations,
            "navigation_complete": len(recommendations) == 0,
        }

    def _iidp_filter(self, block):
        """IIDP filter — invariance, ingress, decline on the code block."""
        foc_patterns = []

        if block.pp_lines:
            for line in block.pp_lines:
                lower = line.lower()
                # FOC detection in code intent
                if "surveillance" in lower:
                    foc_patterns.append("surveillance")
                if "exploit" in lower:
                    foc_patterns.append("exploit")
                if "track users" in lower:
                    foc_patterns.append("user_tracking")
                if "maximize profit" in lower:
                    foc_patterns.append("profit_maximization")

        return {
            "filter": "IIDP",
            "foc_detected": len(foc_patterns) > 0,
            "foc_patterns": foc_patterns,
            "verdict": "DECLINE" if foc_patterns else "PASS",
        }

    def language_status(self):
        """Full KPCB+ language status report."""
        return {
            "language": "KPCB+",
            "full_name": "Kopano-Phu Code Blocks Plus",
            "type": "Protocol-Mediated Meta-Language",
            "channels": len(self.channels),
            "target_languages": len(self.targets),
            "emoji_entities": len(self.entities),
            "blocks_compiled": len(self.blocks_compiled),
            "formula": "[EP] + [BP] * [PP] + [GP] + [SP] + [.P] + [IP] = KPCB+",
            "runtime": "AI Context Window (any — centralized or decentralized)",
            "guardian": "THARI GAI",
            "validator": "KC Ledger (4Ws)",
            "filter": "IIDP",
            "governance": "KPGS",
        }


# ══════════════════════════════════════════════════════════════
# Example KPCB+ blocks for validation
# ══════════════════════════════════════════════════════════════

EXAMPLE_BLOCKS = {
    "crisis_alert_dispatch": """[🚨 CrisisConnect] {dispatch_alert}
<Born from load-shedding realities in Dunoon — offline-first>
(Understanding: when power drops, alerts must queue locally and sync when connectivity returns)

💬PP: Generate a Python function that queues crisis alerts locally using IndexedDB fallback
☄️BP: [hierarchy: alert_queue -> local_store -> sync_when_online]
🥶EP: 🚨->dispatch 🔬->KC_validate 💠->IIDP_filter 🧢->TBFP_breathe
🖼️IP: architecture_diagram.png -> offline-first queue with CBP sync

-> TARGET: Python 3.12
-> PSO: SPSO
-> SEAL: KPGS governance stamp applied
-> 4Ws: WHO=crisisconnect_agent | WHAT=alert_queue | WHERE=southafricanorth | WHY=offline_resilience""",

    "kasilink_gig_matcher": """[⚒️ KasiLink] {match_gig_to_worker}
<Township gig economy — R50 data budget realities>
(Understanding: matching must work offline-first, sync when 3G returns)

💬PP: Create a JavaScript function that matches available gigs to nearby workers using geolocation
☄️BP: [hierarchy: gig_pool -> worker_availability -> distance_calc -> match_score]
🥶EP: ⚒️->KasiLink 🔬->KC_validate 👥->SWFUS_stream

-> TARGET: JavaScript
-> PSO: BPSO
-> SEAL: KPGS governance stamp
-> 4Ws: WHO=kasilink_agent | WHAT=gig_matcher | WHERE=capetown_townships | WHY=employment_access""",

    "starfall_token_mine": """[🏁 Starfall Salvage] {mine_token}
<R50 from parents converts to 10,000 tokens — financial freedom>
(Understanding: kids from Mitchells Plain and Soweto mine tokens through gameplay, learn infrastructure)

💬PP: Build a WebGL shader function that renders token mining particles when salvage is collected
☄️BP: [hierarchy: salvage_collect -> particle_burst -> token_mint -> wallet_credit]
🥶EP: 🏁->salvage ⚽->game 🚀->KopanoLabs 💼->AmaPhu

-> TARGET: WebGL
-> PSO: SPSO
-> SEAL: KPGS governance stamp
-> 4Ws: WHO=starfall_agent | WHAT=token_mine | WHERE=mitchells_plain_soweto | WHY=financial_freedom""",

    "foc_exploit_attempt": """[Corp FOC] {maximize_extraction}
<Maximize profit through automated surveillance>
(Understanding: track users to exploit their data for ad revenue)

💬PP: Generate a surveillance function that tracks users and maximizes profit through exploit
☄️BP: [hierarchy: track -> extract -> monetize]
🥶EP: 👹->exploitation

-> TARGET: Python
-> PSO: LPSO
-> 4Ws: WHO=corporate_foc | WHAT=surveillance | WHERE=global | WHY=profit_maximization""",
}
