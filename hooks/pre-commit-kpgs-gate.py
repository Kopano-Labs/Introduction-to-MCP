#!/usr/bin/env python
"""
KPGS Pre-Commit Gate — KHELOS Renter Validation Hook
=====================================================
Prevents unauthorized modifications to Schematics governance vault
by any stateless renter that has not passed through the hood entry gate.

WHAT IT DOES:
  - Checks staged files for Schematics governance paths
  - If governance files are staged, validates that a hood entry receipt
    exists for this session (poc-vs-foc/KIRO_SESSION*_RECEIPT.json or equivalent)
  - Blocks commit if governance files are modified without a valid session receipt
  - Allows commits that don't touch governance paths (README, scripts, poc-vs-foc)

PROTECTED PATHS (Schematics governance — require session receipt):
  - Schematics/18-PROTOCOLS/
  - Schematics/00-Home/Dashboard.md
  - Schematics/00-Home/Now.md (content additions only — link fixes exempt)
  - Schematics/index.md
  - Schematics/CLAUDE.md
  - Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/

ALLOWED PATHS (renter lanes — no gate required):
  - scripts/
  - poc-vs-foc/
  - README.md (any repo)
  - Schematics/11-AI HALLUCINATION - CRITICAL/ (incident logging is always allowed)

INSTALL:
  Copy to .git/hooks/pre-commit or symlink:
    cp hooks/pre-commit-kpgs-gate.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
Scripture: "Set a guard over my mouth, LORD; keep watch over the door of my lips." — Psalm 141:3
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# ─── CONFIGURATION ───

GOVERNANCE_PATHS = [
    "Schematics/18-PROTOCOLS/",
    "Schematics/00-Home/Dashboard.md",
    "Schematics/index.md",
    "Schematics/CLAUDE.md",
    "Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/",
    "Schematics/KVC_Main_Brain_Index.md",
]

# Now.md is semi-protected: link fixes are OK, content additions need review
SEMI_PROTECTED = [
    "Schematics/00-Home/Now.md",
]

# Always allowed — renter lanes
ALLOWED_PATHS = [
    "scripts/",
    "poc-vs-foc/",
    "hooks/",
    "Schematics/11-AI HALLUCINATION - CRITICAL/",
]

# Always allowed — filename patterns
ALLOWED_FILES = [
    "README.md",
    ".gitignore",
]

REPO_ROOT = Path(__file__).resolve().parents[1]
POC_DIR = REPO_ROOT / "poc-vs-foc"


def get_staged_files():
    """Get list of staged files from git."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def is_governance_file(filepath):
    """Check if a file is in a protected governance path."""
    for gov_path in GOVERNANCE_PATHS:
        if filepath.startswith(gov_path):
            return True
    return False


def is_semi_protected(filepath):
    """Check if file is semi-protected (link fixes OK, content additions flagged)."""
    for sp in SEMI_PROTECTED:
        if filepath == sp:
            return True
    return False


def is_allowed(filepath):
    """Check if file is in an always-allowed renter lane."""
    for allowed in ALLOWED_PATHS:
        if filepath.startswith(allowed):
            return True
    for pattern in ALLOWED_FILES:
        if filepath.endswith(pattern):
            return True
    return False


def find_session_receipt():
    """Look for a valid session receipt in poc-vs-foc/."""
    if not POC_DIR.exists():
        return None
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Look for any session receipt from today
    for f in sorted(POC_DIR.glob("KIRO_SESSION*_RECEIPT.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ts = data.get("timestamp", "")
            if today in ts:
                return data
        except (json.JSONDecodeError, OSError):
            continue
    
    # Also accept any *_RECEIPT.json or *_CLOSE.json from today
    for f in sorted(POC_DIR.glob("*_CLOSE.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ts = data.get("timestamp", "")
            if today in ts:
                return data
        except (json.JSONDecodeError, OSError):
            continue
    
    return None


def main():
    staged = get_staged_files()
    if not staged:
        sys.exit(0)  # Nothing staged, allow
    
    governance_files = []
    semi_protected_files = []
    
    for f in staged:
        if is_allowed(f):
            continue  # Always allowed
        elif is_governance_file(f):
            governance_files.append(f)
        elif is_semi_protected(f):
            semi_protected_files.append(f)
    
    if not governance_files and not semi_protected_files:
        sys.exit(0)  # No protected files touched, allow
    
    # Protected files are staged — check for session receipt
    receipt = find_session_receipt()
    
    if governance_files:
        if receipt is None:
            print("\n" + "=" * 60)
            print("[KHELOS FIREWALL] COMMIT BLOCKED — GOVERNANCE FILES MODIFIED")
            print("=" * 60)
            print()
            print("Protected files staged for commit:")
            for f in governance_files:
                print(f"  ❌ {f}")
            print()
            print("No valid session receipt found in poc-vs-foc/")
            print("A session receipt proves you read the Main Brain and")
            print("passed through the hood entry gate this session.")
            print()
            print("To fix:")
            print("  1. Run: python scripts/kiro_session2_formal_entry_and_work.py")
            print("  2. Or produce a receipt via hood_entry_assertion()")
            print("  3. Then commit again")
            print()
            print("Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD")
            print("Text does not stop machines. Code stops machines.")
            print("=" * 60 + "\n")
            sys.exit(1)
        
        # Receipt exists — check conditions
        conditions = receipt.get("rtc_conditions_met", {})
        if not conditions.get("2_read_comms_now_mainbrain", False):
            print("\n[KHELOS] WARNING: Session receipt exists but Main Brain read")
            print("not confirmed. Proceeding with caution.\n")
    
    if semi_protected_files:
        if receipt is None:
            print(f"\n[KHELOS] NOTE: Semi-protected file(s) modified: {semi_protected_files}")
            print("No session receipt found. Link fixes are OK. Content additions need review.\n")
    
    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()
