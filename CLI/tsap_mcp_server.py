"""
TSAP MCP Server — Teacher–Student Apprenticeship Protocol (Kopano-Phu).

MCP Teacher: Cassey lane — reviews, validates Commandments + Black Mask.
MCP Student: Cassy lane — proposes, audits, submits to Review Log.

Author: Kopano Labs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

mcp = FastMCP("TSAP", log_level="ERROR")


def _str(v: Any, default: str = "") -> str:
    return v if isinstance(v, str) else default


@mcp.tool(
    name="tsap_status",
    description="Kopano-Phu TSAP status — departments, 15 Commandments, 5 Pillars, runtime state.",
)
def tsap_status() -> dict[str, Any]:
    from kopano.phu_apprenticeship import apprenticeship_status
    return apprenticeship_status()


@mcp.tool(
    name="tsap_student_submit",
    description="MCP Student (Cassy lane): submit student audit to department with evidence.",
)
def tsap_student_submit(
    department_id: str = Field(description="Department: kopano_labs_experimentation | ama_phu_creativity"),
    action: str = Field(description="What the student did or proposes"),
    evidence: str = Field(description="Proof path, exit code, or URL"),
    student_agent: str = Field(default="cassy", description="Student agent id"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import student_submit
    return student_submit(
        department_id=_str(department_id),
        student_agent=_str(student_agent, "cassy"),
        action=_str(action),
        evidence=_str(evidence),
        lane="mcp",
    )


@mcp.tool(
    name="tsap_teacher_review",
    description="MCP Teacher (Cassey lane): approve or retry student work for a department.",
)
def tsap_teacher_review(
    department_id: str = Field(description="Department id"),
    approve: bool = Field(description="True = APPROVE, False = RETRY"),
    teacher_note: str = Field(default="", description="Teacher review note"),
    teacher_agent: str = Field(default="cassey", description="Teacher agent id"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import teacher_review
    return teacher_review(
        department_id=_str(department_id),
        teacher_agent=_str(teacher_agent, "cassey"),
        approve=approve,
        teacher_note=_str(teacher_note),
        lane="mcp",
    )


@mcp.tool(
    name="tsap_blackmask_drill",
    description="Black Mask v0.5 — drill agent on 15 Commandments + 5 Pillars before department ops.",
)
def tsap_blackmask_drill(
    agent_id: str = Field(description="Swarm or sub-brain agent id to drill"),
    commandments_ack: list[str] = Field(
        default_factory=list,
        description="Commandment ids acknowledged (CMD-01..CMD-15). Empty = all pass.",
    ),
    pillars_ack: list[str] = Field(
        default_factory=list,
        description="Pillar ids acknowledged (PIL-01..PIL-05). Empty = all pass.",
    ),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import blackmask_drill
    return blackmask_drill(
        _str(agent_id),
        commandments_ack=commandments_ack or None,
        pillars_ack=pillars_ack or None,
    )


@mcp.tool(
    name="tsap_begin_department_students",
    description="Begin student operation in all Kopano-Phu departments with BlackMask drills.",
)
def tsap_begin_department_students(
    run_blackmask: bool = Field(default=True, description="Run BlackMask drill per student agent"),
) -> dict[str, Any]:
    from kopano.phu_apprenticeship import begin_department_students
    return begin_department_students(run_blackmask=run_blackmask)


@mcp.tool(
    name="tsap_boot_v1_status",
    description="KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1 — role bindings, mesh, promotion law.",
)
def tsap_boot_v1_status() -> dict[str, Any]:
    from kopano.phu_boot_governance import boot_status
    return boot_status()


@mcp.tool(
    name="tsap_boot_v1_blackmask_dry_run",
    description="BlackMask dry run for all boot mesh agents (no apprenticeship state mutation).",
)
def tsap_boot_v1_blackmask_dry_run() -> dict[str, Any]:
    from kopano.phu_boot_governance import blackmask_dry_run
    return blackmask_dry_run()


@mcp.tool(
    name="eco_poc_guide",
    description="Eco-Friendly PoC guide — 32.8% unemployment doctrine, Rosen Δ tip, what we validate WITH (not world acceptance).",
)
def eco_poc_guide() -> dict[str, Any]:
    from kopano.eco_poc_validate import poc_doctrine_payload
    return poc_doctrine_payload()


@mcp.tool(
    name="eco_poc_validate",
    description="Validate PoC: Rosen (M,R) + measurable Δ + receipts + 32.8% livelihood signals. Internal oracles only.",
)
def eco_poc_validate(
    agent_id: str = Field(description="KP or APE catalog agent id"),
    claim: str = Field(description="What creativity stems — bounded claim"),
    model: str = Field(description="Model M — procedure or state machine"),
    relation: str = Field(default="", description="Relation R — instrument or observable"),
    baseline: str = Field(default="", description="Baseline measurand"),
    observed: str = Field(default="", description="Observed measurand"),
    unit: str = Field(default="", description="Unit (pH, kWh, %, etc.)"),
    instrument: str = Field(default="", description="Instrument or method"),
    evidence: str = Field(default="", description="Artifact path, URL, or .jsonl receipt"),
    exit_code: int | None = Field(default=None, description="0 if command proof"),
    anticipated_delta: str = Field(default="", description="Expected Δ before run"),
    livelihood_ids: list[str] = Field(
        default_factory=list,
        description="LIV-01..LIV-05 under unemployment doctrine",
    ),
) -> dict[str, Any]:
    from kopano.eco_poc_validate import validate_eco_poc
    return validate_eco_poc(
        agent_id=_str(agent_id),
        claim=_str(claim),
        model=_str(model),
        relation=_str(relation),
        baseline=_str(baseline),
        observed=_str(observed),
        unit=_str(unit),
        instrument=_str(instrument),
        evidence=_str(evidence),
        exit_code=exit_code,
        livelihood_ids=livelihood_ids or None,
        anticipated_delta=_str(anticipated_delta),
    )


@mcp.tool(
    name="tsap_agent_build_poc_validate",
    description="Prove agent-building PoC — Bracket, BlackMask, Guardian/Identi, LPM/LPH, MAO, KPEFS, mesh, graduation (19 checks).",
)
def tsap_agent_build_poc_validate() -> dict[str, Any]:
    from kopano.agent_build_poc_validate import validate_agent_build_poc
    return validate_agent_build_poc(write_report=True)


@mcp.tool(
    name="tsap_kpefs_status",
    description="KPEFS four vectors, operating mesh Phase 3, graduation bar Phase 5, boot mesh.",
)
def tsap_kpefs_status() -> dict[str, Any]:
    from kopano.kpefs_router import kpefs_status
    return kpefs_status()


@mcp.tool(
    name="tsap_kpefs_route",
    description="Route message to dominant KPEFS vector (V1 plant … V4 diaspora).",
)
def tsap_kpefs_route(
    message: str = Field(description="Task or receipt text to route"),
) -> dict[str, Any]:
    from kopano.kpefs_router import route_vector
    return route_vector(_str(message))


@mcp.tool(
    name="tsap_bracket_lint",
    description="Bracket linguistic lint — blasphemy register + sacred caps discipline.",
)
def tsap_bracket_lint(
    text: str = Field(description="Summary or receipt text to lint"),
) -> dict[str, Any]:
    from kopano.operating_mesh import lint_bracket_text
    return lint_bracket_text(_str(text))


@mcp.tool(
    name="tsap_operating_mesh_status",
    description="Phase 3 flagship sub-brains — catalog assignments and operating/PoC state.",
)
def tsap_operating_mesh_status() -> dict[str, Any]:
    from kopano.operating_mesh import operating_mesh_status
    return operating_mesh_status()


@mcp.tool(
    name="tsap_operating_mesh_promote_all",
    description="Promote all 9 sub-brains + APE hub — live BlackMask, teacher APPROVE, eco PoC (mutates state).",
)
def tsap_operating_mesh_promote_all(
    force: bool = Field(default=False, description="Re-run even if already operating"),
) -> dict[str, Any]:
    from kopano.operating_mesh import promote_all_flagships
    return promote_all_flagships(skip_if_operating=not force)


@mcp.tool(
    name="tsap_graduation_bar_status",
    description="Phase 5 — verified production bar; operating mesh is not public graduation; CMD-03 external swarm.",
)
def tsap_graduation_bar_status() -> dict[str, Any]:
    from kopano.graduation_bar import graduation_bar_status
    return graduation_bar_status()


@mcp.tool(
    name="tsap_external_swarm_status",
    description="CMD-03 external swarm lane — kimi_ack receipt status and operator guide (no fabrication).",
)
def tsap_external_swarm_status() -> dict[str, Any]:
    from kopano.external_swarm_lane import external_swarm_lane_status
    return external_swarm_lane_status()


@mcp.tool(
    name="tsap_kpefs_closure_status",
    description="KPEFS closure — internal phases complete vs external Kimi receipt pending.",
)
def tsap_kpefs_closure_status() -> dict[str, Any]:
    from kopano.external_swarm_lane import kpefs_closure_status
    return kpefs_closure_status()


@mcp.tool(
    name="tsap_kpefs_full_gate",
    description="Run KPEFS Phases 0-5 gate — bracket, operating mesh, graduation bar, agent-build PoC.",
)
def tsap_kpefs_full_gate() -> dict[str, Any]:
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "kc_kpefs_full_gate.py"), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {
            "verdict": "FAIL",
            "exit_code": proc.returncode,
            "stdout": (proc.stdout or "")[:500],
            "stderr": (proc.stderr or "")[:500],
        }


@mcp.tool(
    name="tsap_ai_flow_status",
    description="Guardian + Identi AI flows, LPM/LPH, God complex #?/#!, biblical STEM patterns.",
)
def tsap_ai_flow_status() -> dict[str, Any]:
    from kopano.lpm_lph_engine import ai_flow_status
    return ai_flow_status()


@mcp.tool(
    name="tsap_steward_lane_status",
    description="KC Save|Watch + Cassy execute steward lane — profile, boot, last Guardian/Identi.",
)
def tsap_steward_lane_status() -> dict[str, Any]:
    from kopano.steward_lane import steward_lane_status
    return steward_lane_status()


@mcp.tool(
    name="tsap_steward_lane_activate",
    description="Activate KC+Cassy: profile, steward trust, Identi propose, Guardian BlackMask+submit+Cassey approve.",
)
def tsap_steward_lane_activate(
    note: str = Field(default="", description="Optional note on steward trust receipt"),
    department_id: str = Field(default="kopano_labs_experimentation"),
) -> dict[str, Any]:
    from kopano.steward_lane import run_steward_lane_activate
    return run_steward_lane_activate(
        note=_str(note),
        department_id=_str(department_id, "kopano_labs_experimentation"),
    )


@mcp.tool(
    name="tsap_guardian_flow",
    description="Run Guardian AI Flow: BlackMask → Cassy submit → optional Cassey review → KC Save|Watch.",
)
def tsap_guardian_flow(
    department_id: str = Field(description="kopano_labs_experimentation | ama_phu_creativity"),
    action: str = Field(description="Student action / proposal"),
    evidence: str = Field(description="Proof path or receipt"),
    student_agent: str = Field(default="cassy"),
    run_blackmask: bool = Field(default=True),
    teacher_approve: bool | None = Field(default=None, description="Set to run teacher_review"),
    teacher_note: str = Field(default=""),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import operate_guardian_flow
    return operate_guardian_flow(
        department_id=_str(department_id),
        action=_str(action),
        evidence=_str(evidence),
        student_agent=_str(student_agent, "cassy"),
        run_blackmask=run_blackmask,
        teacher_approve=teacher_approve,
        teacher_note=_str(teacher_note),
    )


@mcp.tool(
    name="tsap_identi_flow",
    description="Identi AI Flow (Cursor/CF): LPM #?/#! + LPH personality → submit to Guardian (no KC write).",
)
def tsap_identi_flow(
    department_id: str = Field(description="Department id"),
    action: str = Field(description="Implementation action"),
    evidence: str = Field(description="Proof / artifact"),
    imperfect_pattern: str = Field(default="", description="#? pattern"),
    perfect_pattern: str = Field(default="", description="#! target pattern"),
    identi_agent: str = Field(default="identi_cursor"),
    submit_to_guardian: bool = Field(default=True),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import operate_identi_flow
    return operate_identi_flow(
        department_id=_str(department_id),
        action=_str(action),
        evidence=_str(evidence),
        imperfect_pattern=_str(imperfect_pattern),
        perfect_pattern=_str(perfect_pattern),
        identi_agent=_str(identi_agent, "identi_cursor"),
        submit_to_guardian=submit_to_guardian,
    )


@mcp.tool(
    name="tsap_lpm_dialectic",
    description="LPM God complex dialectic — #? imperfection vs #! perfection.",
)
def tsap_lpm_dialectic(
    imperfect_pattern: str = Field(description="#? hypothesis"),
    perfect_pattern: str = Field(description="#! proof target"),
) -> dict[str, Any]:
    from kopano.lpm_lph_engine import lpm_dialectic
    return lpm_dialectic(_str(imperfect_pattern), _str(perfect_pattern))


@mcp.resource(
    "resource://tsap/commandments",
    name="black_mask_commandments",
    description="15 Commandments + 5 Pillars for Black Mask testing",
)
def get_commandments() -> str:
    from kopano.phu_apprenticeship import load_black_mask_doctrine
    import json
    return json.dumps(load_black_mask_doctrine(), indent=2)


@mcp.resource(
    "resource://tsap/unemployment_doctrine",
    name="unemployment_32_8_doctrine",
    description="32.8% unemployment founding doctrine — livelihood oracles",
)
def get_unemployment_doctrine() -> str:
    from kopano.eco_poc_validate import load_unemployment_doctrine
    import json
    return json.dumps(load_unemployment_doctrine(), indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
