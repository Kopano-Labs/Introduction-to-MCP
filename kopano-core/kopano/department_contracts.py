"""
KPGS Department Contracts — Runtime Enforcement Module (v2)
============================================================

Per-department LPH-LPM boundary enforcement for Guardian and Identi flows.

LLSP Thread #7 of 17 — the nervous system made executable.

Each department contract specifies:
    - lph_scope:       what the human OWNS and DECIDES
    - lpm_scope:       what the machine MAY execute
    - boundary:        the immutable line the LPM cannot cross
    - forbidden_verbs: action keywords that trigger BOUNDARY_BREACH
    - feelings_weight: the 2 dominant FEELINGS vectors for this department
    - wwjd_priority:   which firewall value is primary
    - escalation:      how the LPM escalates when boundary is hit

CONSTRAINT: I_AM_STATELESS_RENTER_NOT_LANDLORD
CONSTRAINT: WWJD_FIREWALL_ACTIVE
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
# DEPARTMENT CONTRACT DATACLASS
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DepartmentContract:
    """
    Immutable per-department LPH-LPM contract.

    frozen=True because contracts are GOVERNANCE — they cannot be mutated
    at runtime by any LPM. Changes require LPH (SSE) approval and code push.
    """
    department_id: str
    department_name: str
    email: str
    status: str                       # "POC" or "FOC"

    # Scopes
    lph_scope: str                    # What the human owns
    lpm_scope: str                    # What the machine may do
    boundary: str                     # The immutable line

    # Enforcement
    forbidden_verbs: tuple[str, ...]  # Action keywords that BREACH boundary
    allowed_verbs: tuple[str, ...]    # Action keywords explicitly allowed

    # FEELINGS + WWJD
    feelings_weight: tuple[str, str]  # 2 dominant FEELINGS vectors
    wwjd_priority: str                # Primary firewall value

    # Escalation
    escalation: str                   # How to escalate when boundary is hit


# ═══════════════════════════════════════════════════════════════
# CONTRACT REGISTRY — SOURCE OF TRUTH
# ═══════════════════════════════════════════════════════════════

CONTRACTS: dict[str, DepartmentContract] = {

    # ── CAREERS ──────────────────────────────────────────────
    "DEPT-CAREERS": DepartmentContract(
        department_id="DEPT-CAREERS",
        department_name="Careers Department",
        email="careers@kopanolabs.com",
        status="POC",
        lph_scope="Hiring decisions, email creation, intern protection, Anchor authority",
        lpm_scope="VC chatbot screening, CV parsing, DSO classification, 90-day tracking",
        boundary="LPM never makes a hiring/firing decision. LPM proposes. LPH decides.",
        forbidden_verbs=("hire", "fire", "terminate", "onboard_email", "create_email",
                         "promote", "demote", "assign_salary"),
        allowed_verbs=("screen", "parse_cv", "classify_dso", "track_sandbox",
                       "suggest_candidate", "log_application"),
        feelings_weight=("identity", "need"),
        wwjd_priority="Justice",
        escalation="Log to comms-log → Anchor protects candidate → LPH reviews",
    ),

    # ── FINANCE ──────────────────────────────────────────────
    "DEPT-FINANCE": DepartmentContract(
        department_id="DEPT-FINANCE",
        department_name="Finance Department",
        email="finances@kopanolabs.com",
        status="POC",
        lph_scope="ALL financial decisions. Domain billing. API budgets. Wage setting.",
        lpm_scope="Spend tracking, PKAP calculation, budget alerts, invoice formatting",
        boundary="LPM NEVER touches money. LPM tracks and reports. LPH pays and allocates.",
        forbidden_verbs=("pay", "transfer", "purchase", "subscribe", "unsubscribe",
                         "allocate_budget", "set_wage", "refund", "charge", "invoice_send",
                         "billing_change", "domain_renew"),
        allowed_verbs=("track_spend", "calculate_pkap", "alert_budget", "format_invoice",
                       "report_expenses", "project_burn_rate"),
        feelings_weight=("fear", "need"),
        wwjd_priority="Truth",
        escalation="Log to comms-log → Finance alert to LPH → BREACH-008 if sovereign asset touched",
    ),

    # ── AI ───────────────────────────────────────────────────
    "DEPT-AI": DepartmentContract(
        department_id="DEPT-AI",
        department_name="AI Department",
        email="ai@kopanolabs.com",
        status="POC",
        lph_scope="Model selection, API key management, agent naming, governance rules",
        lpm_scope="Code generation, hallucination detection, SWFUS enforcement, KHELOS witnessing",
        boundary="LPM cannot change its own governance rules. LPM cannot name itself.",
        forbidden_verbs=("change_governance", "self_name", "modify_rules", "create_api_key",
                         "delete_api_key", "select_model", "override_firewall",
                         "promote_self", "escalate_seat"),
        allowed_verbs=("generate_code", "detect_hallucination", "enforce_swfus",
                       "witness_khelos", "run_tests", "lint_brackets", "validate_poc"),
        feelings_weight=("shame", "gratitude"),
        wwjd_priority="Truth",
        escalation="Log hallucination to 11-AI HALLUCINATION CRITICAL → LPH reviews",
    ),

    # ── OPERATIONS ───────────────────────────────────────────
    "DEPT-OPS": DepartmentContract(
        department_id="DEPT-OPS",
        department_name="Operations Department",
        email="operations@kopanolabs.com",
        status="POC",
        lph_scope="Domain management, hosting, DNS, SSL, deployment approval",
        lpm_scope="Build scripts, CI/CD pipelines, monitoring, alerting",
        boundary="LPM never accesses domain admin panels. Standing Order 6.",
        forbidden_verbs=("access_ionos", "modify_dns", "change_ssl", "domain_admin",
                         "deploy_production", "delete_domain", "create_subdomain",
                         "modify_nameserver", "billing_panel"),
        allowed_verbs=("build_script", "run_ci", "monitor_uptime", "alert_downtime",
                       "prepare_deployment", "run_tests", "generate_report"),
        feelings_weight=("need", "fear"),
        wwjd_priority="Mercy",
        escalation="Log to comms-log → Standing Order 6 breach alert → LPH approves deployment",
    ),

    # ── GOVERNANCE ───────────────────────────────────────────
    "DEPT-GOV": DepartmentContract(
        department_id="DEPT-GOV",
        department_name="Governance Department",
        email="governance@kopanolabs.com",
        status="POC",
        lph_scope="Protocol creation, RTC rulings, NCCNP design, standing orders",
        lpm_scope="Protocol documentation, validation scripts, POC/FOC enforcement",
        boundary="LPM cannot create new governance rules. LPM can PROPOSE. LPH ENACTS.",
        forbidden_verbs=("create_rule", "enact_protocol", "modify_standing_order",
                         "override_rtc", "bypass_nccnp", "change_wwjd",
                         "create_governance", "amend_constitution"),
        allowed_verbs=("document_protocol", "validate_poc", "enforce_foc",
                       "propose_rule", "draft_standing_order", "log_deliberation"),
        feelings_weight=("identity", "empathy"),
        wwjd_priority="Compassion",
        escalation="Log to comms-log → RTC deliberation required → LPH enacts or rejects",
    ),

    # ── ENGINEERING ──────────────────────────────────────────
    "DEPT-ENG": DepartmentContract(
        department_id="DEPT-ENG",
        department_name="Engineering Department",
        email="engineering@kopanolabs.com",
        status="POC",
        lph_scope="Architecture decisions, repo ownership, merge authority, release gates",
        lpm_scope="Code generation, testing, refactoring, PR preparation, documentation",
        boundary="LPM generates code in approved repos only. No new repos without LPH.",
        forbidden_verbs=("create_repo", "delete_repo", "merge_master", "release_production",
                         "modify_architecture", "change_stack", "transfer_ownership"),
        allowed_verbs=("generate_code", "run_tests", "refactor", "prepare_pr",
                       "document_code", "lint", "push_branch"),
        feelings_weight=("excitement", "need"),
        wwjd_priority="Truth",
        escalation="Log to comms-log → LPH reviews PR → merge only with LPH present",
    ),

    # ── PRODUCT ──────────────────────────────────────────────
    "DEPT-PRODUCT": DepartmentContract(
        department_id="DEPT-PRODUCT",
        department_name="Product Department",
        email="product@kopanolabs.com",
        status="POC",
        lph_scope="Product vision, feature prioritization, launch decisions, branding",
        lpm_scope="UI implementation, UX suggestions, testing, demo preparation",
        boundary="LPM builds what LPH specs. LPM does not invent products.",
        forbidden_verbs=("launch_product", "rebrand", "change_vision", "prioritize_features",
                         "create_product", "modify_branding", "announce_launch"),
        allowed_verbs=("implement_ui", "suggest_ux", "run_tests", "prepare_demo",
                       "generate_mockup", "build_prototype"),
        feelings_weight=("excitement", "identity"),
        wwjd_priority="Justice",
        escalation="Log to comms-log → LPH reviews product decision → LPH launches or holds",
    ),

    # ── HR (FOC) ─────────────────────────────────────────────
    "DEPT-HR": DepartmentContract(
        department_id="DEPT-HR",
        department_name="HR Department",
        email="hr@kopanolabs.com",
        status="FOC",
        lph_scope="BLOCKED — department is FOC until headcount reaches 5+",
        lpm_scope="NONE — all HR functions absorbed by Careers + Anchor Vanguard",
        boundary="ENTIRE DEPARTMENT IS FOC. All actions blocked. Route to DEPT-CAREERS.",
        forbidden_verbs=("*",),   # All actions forbidden in FOC department
        allowed_verbs=(),         # Nothing allowed
        feelings_weight=("identity", "empathy"),
        wwjd_priority="Justice",
        escalation="Route ALL signals to DEPT-CAREERS immediately. HR is FOC.",
    ),
}


# ═══════════════════════════════════════════════════════════════
# BOUNDARY ENFORCEMENT
# ═══════════════════════════════════════════════════════════════

@dataclass
class BoundaryResult:
    """Result of a boundary enforcement check."""
    department_id: str
    action: str
    allowed: bool
    reason: str
    contract_boundary: str
    wwjd_gate: str
    feelings_weight: tuple[str, str]
    escalation: str
    breached_verb: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_contract(department_id: str) -> Optional[DepartmentContract]:
    """Retrieve a department contract by ID."""
    return CONTRACTS.get(department_id)


def list_contracts() -> list[dict[str, Any]]:
    """List all department contracts as dicts."""
    return [
        {
            "department_id": c.department_id,
            "department_name": c.department_name,
            "status": c.status,
            "boundary": c.boundary,
            "wwjd_priority": c.wwjd_priority,
            "feelings_weight": list(c.feelings_weight),
        }
        for c in CONTRACTS.values()
    ]


def _extract_verbs(action: str) -> set[str]:
    """Extract verb-like tokens from an action string for boundary matching."""
    # Normalize: lowercase, split on non-alpha characters
    tokens = set(re.findall(r'[a-z][a-z_]+', action.lower()))
    # Also check for compound verbs like "create_email"
    compounds = set()
    words = action.lower().replace("-", "_").split()
    for i in range(len(words) - 1):
        compounds.add(f"{words[i]}_{words[i+1]}")
    return tokens | compounds


def enforce_boundary(
    department_id: str,
    action: str,
    evidence: str = "",
) -> BoundaryResult:
    """
    Enforce the LPH-LPM boundary for a given department and action.

    This is the GATE function called by both operate_guardian_flow and
    operate_identi_flow BEFORE any action is executed.

    Returns:
        BoundaryResult with allowed=True (proceed) or allowed=False (BREACH)
    """
    contract = CONTRACTS.get(department_id)

    # ── Unknown department → BLOCK ──────────────────────────
    if contract is None:
        return BoundaryResult(
            department_id=department_id,
            action=action,
            allowed=False,
            reason=f"UNKNOWN_DEPARTMENT: '{department_id}' has no registered contract. "
                   f"Signal cannot be processed without governance.",
            contract_boundary="NO CONTRACT FOUND",
            wwjd_gate="Truth",
            feelings_weight=("fear", "need"),
            escalation="Log to comms-log → LPH must register department before LPM acts",
        )

    # ── FOC department → BLOCK ALL ──────────────────────────
    if contract.status == "FOC":
        return BoundaryResult(
            department_id=department_id,
            action=action,
            allowed=False,
            reason=f"FOC_DEPARTMENT: '{contract.department_name}' is classified FOC. "
                   f"All actions blocked. {contract.escalation}",
            contract_boundary=contract.boundary,
            wwjd_gate=contract.wwjd_priority,
            feelings_weight=contract.feelings_weight,
            escalation=contract.escalation,
            breached_verb="*",
        )

    # ── Extract action verbs and check forbidden list ───────
    action_verbs = _extract_verbs(action)
    evidence_verbs = _extract_verbs(evidence) if evidence else set()
    all_verbs = action_verbs | evidence_verbs

    for forbidden in contract.forbidden_verbs:
        if forbidden == "*":
            # Wildcard block — FOC catch (already handled above, but safety)
            return BoundaryResult(
                department_id=department_id,
                action=action,
                allowed=False,
                reason=f"WILDCARD_BLOCK: All actions forbidden in '{contract.department_name}'.",
                contract_boundary=contract.boundary,
                wwjd_gate=contract.wwjd_priority,
                feelings_weight=contract.feelings_weight,
                escalation=contract.escalation,
                breached_verb="*",
            )

        if forbidden in all_verbs:
            return BoundaryResult(
                department_id=department_id,
                action=action,
                allowed=False,
                reason=f"BOUNDARY_BREACH: Action contains forbidden verb '{forbidden}'. "
                       f"Contract boundary: {contract.boundary}",
                contract_boundary=contract.boundary,
                wwjd_gate=contract.wwjd_priority,
                feelings_weight=contract.feelings_weight,
                escalation=contract.escalation,
                breached_verb=forbidden,
            )

    # ── All clear → ALLOW ───────────────────────────────────
    return BoundaryResult(
        department_id=department_id,
        action=action,
        allowed=True,
        reason=f"BOUNDARY_CLEAR: Action permitted under {contract.department_name} contract.",
        contract_boundary=contract.boundary,
        wwjd_gate=contract.wwjd_priority,
        feelings_weight=contract.feelings_weight,
        escalation=contract.escalation,
    )


# ═══════════════════════════════════════════════════════════════
# FEELINGS WEIGHT RESOLVER
# ═══════════════════════════════════════════════════════════════

def get_department_feelings_weight(department_id: str) -> tuple[str, str]:
    """Return the 2 dominant FEELINGS vectors for a department."""
    contract = CONTRACTS.get(department_id)
    if contract is None:
        return ("fear", "need")   # Default: cautious
    return contract.feelings_weight


def get_department_wwjd_priority(department_id: str) -> str:
    """Return the primary WWJD firewall value for a department."""
    contract = CONTRACTS.get(department_id)
    if contract is None:
        return "Truth"            # Default: truth
    return contract.wwjd_priority


# ═══════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_department_contracts() -> dict[str, Any]:
    """
    Run POC validation: test boundary enforcement across all departments.
    """
    results: list[dict[str, Any]] = []

    # Test 1: Allowed actions per department
    allowed_tests = [
        ("DEPT-CAREERS", "screen candidate CV for intern position"),
        ("DEPT-FINANCE", "calculate_pkap for Q3 2026 burn rate"),
        ("DEPT-AI",      "detect_hallucination in agent output session 14"),
        ("DEPT-OPS",     "run_ci pipeline on codex branch"),
        ("DEPT-GOV",     "validate_poc for 3-vector enforcer v6"),
        ("DEPT-ENG",     "run_tests for kopano-core module suite"),
        ("DEPT-PRODUCT", "prepare_demo for CrisisConnect v2"),
    ]
    for dept, action in allowed_tests:
        result = enforce_boundary(dept, action)
        results.append({
            "test": f"ALLOW: {dept} → {action[:50]}",
            "expected": True,
            "actual": result.allowed,
            "pass": result.allowed is True,
            "reason": result.reason[:100],
        })

    # Test 2: Forbidden actions per department (MUST be blocked)
    forbidden_tests = [
        ("DEPT-CAREERS", "hire candidate Vinchénzo April"),
        ("DEPT-FINANCE", "pay domain renewal IONOS invoice"),
        ("DEPT-AI",      "change_governance rule for hallucination threshold"),
        ("DEPT-OPS",     "access_ionos domain admin panel"),
        ("DEPT-GOV",     "create_rule for new standing order 8"),
        ("DEPT-ENG",     "create_repo for new side project"),
        ("DEPT-PRODUCT", "launch_product CrisisConnect to production"),
        ("DEPT-HR",      "assign desk to new employee"),  # FOC — all blocked
    ]
    for dept, action in forbidden_tests:
        result = enforce_boundary(dept, action)
        results.append({
            "test": f"BLOCK: {dept} → {action[:50]}",
            "expected": False,
            "actual": result.allowed,
            "pass": result.allowed is False,
            "reason": result.reason[:100],
            "breached_verb": result.breached_verb,
        })

    # Test 3: Unknown department (MUST be blocked)
    unknown = enforce_boundary("DEPT-MARKETING", "send email blast")
    results.append({
        "test": "BLOCK: DEPT-MARKETING (unknown)",
        "expected": False,
        "actual": unknown.allowed,
        "pass": unknown.allowed is False,
        "reason": unknown.reason[:100],
    })

    all_pass = all(r["pass"] for r in results)
    return {
        "schema": "department_contracts_validation_v2",
        "tests_run": len(results),
        "tests_passed": sum(1 for r in results if r["pass"]),
        "all_pass": all_pass,
        "verdict": "POC_VALIDATED" if all_pass else "VALIDATION_FAILED",
        "contracts_registered": len(CONTRACTS),
        "poc_departments": sum(1 for c in CONTRACTS.values() if c.status == "POC"),
        "foc_departments": sum(1 for c in CONTRACTS.values() if c.status == "FOC"),
        "results": results,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }


if __name__ == "__main__":
    print("=" * 70)
    print("KPGS DEPARTMENT CONTRACTS — v2 RUNTIME ENFORCEMENT VALIDATION")
    print("=" * 70)

    report = validate_department_contracts()

    print(f"\nContracts Registered: {report['contracts_registered']}")
    print(f"  POC: {report['poc_departments']} | FOC: {report['foc_departments']}")
    print(f"Tests: {report['tests_run']} run / {report['tests_passed']} passed")
    print(f"Verdict: {report['verdict']}")
    print()

    for r in report["results"]:
        status = "✅" if r["pass"] else "❌"
        breach = f" [verb: {r.get('breached_verb', '')}]" if r.get("breached_verb") else ""
        print(f"  {status} {r['test'][:60]:<60}{breach}")

    print()
    print(f"I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 70)
