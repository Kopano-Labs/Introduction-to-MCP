"""Kopano-Phu legacy API — Cassy under Kopano Labs + Ama-Phu; Bracket Protocol."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from .operator_auth import require_operator
from .eco_poc_validate import poc_doctrine_payload, validate_eco_poc
from .kpefs_router import kpefs_status, route_vector
from .operating_mesh import (
    lint_bracket_text,
    operating_mesh_status,
    promote_all_flagships,
    promote_flagship,
)
from .graduation_bar import (
    graduation_bar_status,
    graduation_claim_allowed,
    record_steward_trust,
    run_guard_verified_production,
)
from .external_swarm_lane import (
    external_swarm_lane_status,
    kpefs_closure_status,
    validate_evidence_url,
)
from .lpm_lph_engine import (
    ai_flow_status,
    attach_lpm_to_mao,
    lpm_dialectic,
    operate_guardian_flow,
    operate_identi_flow,
    select_lph_personality,
)
from .steward_lane import run_steward_lane_activate, steward_lane_status
from .kpgs_governance import compile_kpgs_governance, governance_status, propagate_governance_marker
from .kpgs_renter_entry import assert_and_log_entry, hood_entry_assertion, load_renter_entryway
from .kpgs_spawn_swarm import (
    compile_spawn_swarm,
    forensic_sociology_classify,
    spawn_swarm_status,
    swfus_envelope,
    validate_spawn_swarm,
)
from .infinite_hood_cloud import (
    compile_infinite_hood,
    hood_dispatch_for_plot,
    infinite_hood_status,
    load_deployment_manifest,
    load_domain_grid,
    outer_api_surface,
)
from .kpgs_activation_gate import check_kpgs_activation_gate
from .kpgs_behavioral_poc import run_kpgs_behavioral_poc, run_sovereign_sim_tick
from .sovereign_sim import (
    bootstrap_sovereign_sim,
    run_kpgs_smoke_poc,
    sovereign_sim_status,
    sovereign_sim_ui_snapshot,
)
from .phu_boot_governance import (
    apply_boot,
    blackmask_dry_run,
    boot_status,
    mesh_summary,
    promotion_allowed,
)
from .phu_apprenticeship import (
    apprenticeship_status,
    begin_department_students,
    blackmask_drill,
    student_submit,
    teacher_review,
)
from .phu_ecosystem import (
    bracket_protocol_status,
    ecosystem_payload,
    main_brain_index,
    merge_sub_brain_rows,
    populate_main_brain,
    reattach_detached_subbrains,
)

router = APIRouter(prefix="/api/kc/phu", tags=["kopano-phu-legacy"])


class PhuReattachBody(BaseModel):
    dry_run: bool = Field(default=False)


class PhuPopulateBody(BaseModel):
    sync_vault_logs: bool = Field(default=True)


class TsapStudentBody(BaseModel):
    department_id: str
    action: str
    evidence: str
    student_agent: str = "cassy"


class TsapTeacherBody(BaseModel):
    department_id: str
    approve: bool
    teacher_note: str = ""
    teacher_agent: str = "cassey"


class TsapBlackMaskBody(BaseModel):
    agent_id: str


class TsapBeginBody(BaseModel):
    run_blackmask: bool = True


class GuardianFlowBody(BaseModel):
    department_id: str
    action: str
    evidence: str
    student_agent: str = "cassy"
    run_blackmask: bool = True
    teacher_approve: bool | None = None
    teacher_note: str = ""


class IdentiFlowBody(BaseModel):
    department_id: str
    action: str
    evidence: str
    imperfect_pattern: str = ""
    perfect_pattern: str = ""
    identi_agent: str = "identi_cursor"
    submit_to_guardian: bool = True


class LpmDialecticBody(BaseModel):
    imperfect_pattern: str
    perfect_pattern: str


class EcoPocValidateBody(BaseModel):
    agent_id: str
    claim: str
    model: str
    relation: str = ""
    baseline: str = ""
    observed: str = ""
    unit: str = ""
    instrument: str = ""
    evidence: str = ""
    exit_code: int | None = None
    anticipated_delta: str = ""
    livelihood_ids: list[str] = Field(default_factory=list)


def _require_god(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    return require_operator(authorization, god_only=True)


@router.get("/ecosystem")
def get_ecosystem() -> dict:
    """Full Kopano-Phu status — sub-brains, Main Brain index, Bracket Protocol."""
    return ecosystem_payload()


@router.get("/bracket-protocol")
def get_bracket_protocol() -> dict:
    return bracket_protocol_status()


@router.get("/main-brain/index")
def get_main_brain_index() -> dict:
    return main_brain_index()


@router.get("/sub-brains")
def list_sub_brains() -> dict:
    return {"sub_brains": merge_sub_brain_rows()}


@router.post("/reattach-subbrains")
def post_reattach(
    body: PhuReattachBody,
    operator: dict = Depends(_require_god),
) -> dict:
    """Reattach unused/detached sub-brains to Cassy legacy lane."""
    result = reattach_detached_subbrains(dry_run=body.dry_run)
    return {"operator": operator["email"], **result}


@router.get("/apprenticeship/status")
def get_apprenticeship_status() -> dict:
    """TSAP status — MCP/MAO teacher-student lanes, departments, Black Mask doctrine."""
    return apprenticeship_status()


@router.post("/apprenticeship/begin-students")
def post_begin_students(body: TsapBeginBody) -> dict:
    """Begin student operation in all Kopano-Phu departments."""
    return begin_department_students(run_blackmask=body.run_blackmask)


@router.post("/apprenticeship/student-submit")
def post_student_submit(body: TsapStudentBody) -> dict:
    return student_submit(
        department_id=body.department_id,
        student_agent=body.student_agent,
        action=body.action,
        evidence=body.evidence,
        lane="api",
    )


@router.post("/apprenticeship/teacher-review")
def post_teacher_review(body: TsapTeacherBody) -> dict:
    return teacher_review(
        department_id=body.department_id,
        teacher_agent=body.teacher_agent,
        approve=body.approve,
        teacher_note=body.teacher_note,
        lane="api",
    )


@router.post("/apprenticeship/blackmask-drill")
def post_blackmask_drill(body: TsapBlackMaskBody) -> dict:
    return blackmask_drill(body.agent_id)


@router.get("/poc/guide")
def get_poc_guide() -> dict:
    """Eco-Friendly PoC guide — 32.8% doctrine, Rosen Δ tip, internal oracles (not world acceptance)."""
    return poc_doctrine_payload()


@router.get("/kpefs/status")
def get_kpefs_status() -> dict:
    """KPEFS — four vectors, boot mesh, implementation plan refs."""
    return kpefs_status()


@router.post("/kpefs/route")
def post_kpefs_route(body: dict) -> dict:
    msg = str(body.get("message", ""))
    return route_vector(msg)


@router.post("/bracket-lint")
def post_bracket_lint(body: dict) -> dict:
    """Lint bracket tags in submit text (Studio + API)."""
    return lint_bracket_text(str(body.get("text", "")))


@router.get("/operating-mesh/status")
def get_operating_mesh_status() -> dict:
    """Phase 3 — flagship sub-brain operating mesh."""
    return operating_mesh_status()


@router.post("/operating-mesh/promote-all")
def post_operating_mesh_promote_all(
    operator: dict = Depends(_require_god),
) -> dict:
    """Promote all flagships with live BlackMask + teacher APPROVE + PoC (god mode)."""
    return {"operator": operator["email"], **promote_all_flagships()}


@router.post("/operating-mesh/promote/{sub_brain_id}")
def post_operating_mesh_promote_one(
    sub_brain_id: str,
    operator: dict = Depends(_require_god),
) -> dict:
    return {"operator": operator["email"], **promote_flagship(sub_brain_id, skip_if_operating=False)}


@router.get("/graduation-bar/status")
def get_graduation_bar_status() -> dict:
    """Phase 5 — verified production bar; operating mesh ≠ graduation."""
    return graduation_bar_status()


@router.post("/graduation-bar/check-claim")
def post_graduation_check_claim(body: dict) -> dict:
    return graduation_claim_allowed(claim=str(body.get("claim", "")))


@router.post("/graduation-bar/steward-trust")
def post_graduation_steward_trust(
    body: dict | None = None,
    operator: dict = Depends(_require_god),
) -> dict:
    note = str((body or {}).get("note", ""))
    return {"operator": operator["email"], **record_steward_trust(note=note)}


@router.get("/steward-lane/status")
def get_steward_lane_status() -> dict:
    """KC Save|Watch + Cassy execute — profile, boot, last AI flows."""
    return steward_lane_status()


@router.get("/steward-lane/kasilink-snapshot")
def get_steward_lane_kasilink_snapshot() -> dict:
    """KasiLink UI snapshot — Main Brain comms + steward status."""
    from .steward_lane import steward_lane_kasilink_snapshot

    return steward_lane_kasilink_snapshot()


@router.post("/steward-lane/activate")
def post_steward_lane_activate(
    body: dict | None = None,
    operator: dict = Depends(_require_god),
) -> dict:
    """Activate Cassy profile, steward trust, Identi → Guardian (Cassey approve)."""
    b = body or {}
    return {
        "operator": operator["email"],
        **run_steward_lane_activate(
            note=str(b.get("note", "Studio steward lane activate")),
            department_id=str(b.get("department_id", "kopano_labs_experimentation")),
            run_identi=bool(b.get("run_identi", True)),
            run_guardian=bool(b.get("run_guardian", True)),
            teacher_approve=bool(b.get("teacher_approve", True)),
            action=str(b["action"]) if b.get("action") else None,
            evidence=str(b["evidence"]) if b.get("evidence") else None,
        ),
    }


@router.post("/graduation-bar/guard")
def post_graduation_guard(
    operator: dict = Depends(_require_god),
) -> dict:
    return {"operator": operator["email"], **run_guard_verified_production()}


@router.get("/external-swarm/status")
def get_external_swarm_status() -> dict:
    """CMD-03 — Kimi / external orchestrator manual receipt lane."""
    return external_swarm_lane_status()


@router.post("/external-swarm/validate-url")
def post_external_swarm_validate_url(body: dict) -> dict:
    return validate_evidence_url(str(body.get("url", "")))


@router.get("/closure/status")
def get_kpefs_closure_status() -> dict:
    """Internal KPEFS complete vs external swarm receipt pending."""
    return kpefs_closure_status()


@router.get("/ai-flow/status")
def get_ai_flow_status() -> dict:
    """Guardian + Identi flows, LPM/LPH, BlackMask/TSAP summary."""
    return ai_flow_status()


@router.post("/ai-flow/guardian")
def post_guardian_flow(body: GuardianFlowBody) -> dict:
    """Guardian AI Flow — KC+Cassy+Cassey with BlackMask + TSAP."""
    return operate_guardian_flow(
        department_id=body.department_id,
        action=body.action,
        evidence=body.evidence,
        student_agent=body.student_agent,
        run_blackmask=body.run_blackmask,
        teacher_approve=body.teacher_approve,
        teacher_note=body.teacher_note,
    )


@router.post("/ai-flow/identi")
def post_identi_flow(body: IdentiFlowBody) -> dict:
    """Identi AI Flow — LPM #?/#! + LPH code-switch → handoff to Guardian."""
    return operate_identi_flow(
        department_id=body.department_id,
        action=body.action,
        evidence=body.evidence,
        imperfect_pattern=body.imperfect_pattern,
        perfect_pattern=body.perfect_pattern,
        identi_agent=body.identi_agent,
        submit_to_guardian=body.submit_to_guardian,
    )


@router.post("/lpm/dialectic")
def post_lpm_dialectic(body: LpmDialecticBody) -> dict:
    return lpm_dialectic(body.imperfect_pattern, body.perfect_pattern)


@router.post("/lpm/attach-mao")
def post_lpm_attach_mao(body: dict) -> dict:
    msg = str(body.get("message", ""))
    intent = str(body.get("intent", "execute"))
    return attach_lpm_to_mao(msg, intent=intent)


@router.post("/lph/select")
def post_lph_select(body: dict) -> dict:
    return select_lph_personality(str(body.get("message", "")))


@router.get("/boot/v1")
def get_boot_v1() -> dict:
    """KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1 governance status."""
    return boot_status()


@router.post("/boot/v1/apply")
def post_boot_v1_apply() -> dict:
    return apply_boot()


@router.post("/boot/v1/blackmask-dry-run")
def post_boot_blackmask_dry_run() -> dict:
    return blackmask_dry_run()


@router.get("/boot/v1/mesh")
def get_boot_mesh() -> dict:
    return mesh_summary()


@router.get("/kpgs/entry")
def get_kpgs_hood_entry() -> dict:
    """Stateless renter entryway — who you are fucking with on hood entry."""
    return hood_entry_assertion()


@router.post("/kpgs/entry/assert")
def post_kpgs_hood_entry_assert(body: dict) -> dict:
    """Log hood entry with renter ack."""
    return assert_and_log_entry(
        renter_id=str(body.get("renter_id", "anonymous")),
        renter_class=str(body.get("renter_class", "linguistic_actor")),
        hood_ack=str(body.get("hood_ack", "")),
    )


@router.get("/kpgs/governance")
def get_kpgs_governance() -> dict:
    """Schematics MAIN BRAIN governance status."""
    return governance_status()


@router.post("/kpgs/governance/compile")
def post_kpgs_governance_compile() -> dict:
    return compile_kpgs_governance()


@router.post("/kpgs/governance/propagate")
def post_kpgs_governance_propagate() -> dict:
    return propagate_governance_marker()


@router.get("/kpgs/spawn/status")
def get_kpgs_spawn_status() -> dict:
    """300-agent spawn swarm status — altar layers, forensic lenses, SWFUS."""
    return spawn_swarm_status()


@router.post("/kpgs/spawn/compile")
def post_kpgs_spawn_compile() -> dict:
    return compile_spawn_swarm()


@router.post("/kpgs/spawn/validate")
def post_kpgs_spawn_validate() -> dict:
    return validate_spawn_swarm(write_report=True)


@router.post("/kpgs/spawn/swfus")
def post_kpgs_spawn_swfus(body: dict) -> dict:
    return swfus_envelope(
        agent_id=str(body.get("agent_id", "spawn_junior_205")),
        prompt=str(body.get("prompt", "")),
        protocol=str(body.get("protocol", "api")),
    )


@router.post("/kpgs/spawn/forensic")
def post_kpgs_spawn_forensic(body: dict) -> dict:
    return forensic_sociology_classify(
        message=str(body.get("message", "")),
        agent_id=str(body.get("agent_id", "")),
    )


@router.get("/kpgs/hood/status")
def get_infinite_hood_status() -> dict:
    """Infinite Hood — domain-sharded cloud territory status."""
    return infinite_hood_status()


@router.get("/kpgs/hood/domains")
def get_infinite_hood_domains() -> dict:
    """Domain plot inventory + deployment assignment counts."""
    grid = load_domain_grid()
    manifest = load_deployment_manifest()
    return {
        "grid": grid,
        "deployment_summary": {
            "verdict": manifest.get("verdict"),
            "agents_assigned": manifest.get("agents_assigned"),
            "landlords_assigned": manifest.get("landlords_assigned"),
            "by_plot_agent_count": manifest.get("by_plot_agent_count"),
        },
    }


@router.get("/kpgs/hood/outer-api")
def get_infinite_hood_outer_api() -> dict:
    """Outer API ingress map for PWAs, Microsoft, Google clients."""
    return outer_api_surface()


@router.post("/kpgs/hood/compile")
def post_infinite_hood_compile() -> dict:
    return compile_infinite_hood()


@router.post("/kpgs/hood/dispatch")
def post_infinite_hood_dispatch(body: dict) -> dict:
    """Client ingress dispatch — plot → landlord agent → SWFUS event bus."""
    return hood_dispatch_for_plot(
        plot_id=str(body.get("plot_id", "plot_kopano_context")),
        message=str(body.get("message", "")),
        agent_id=str(body.get("agent_id", "")),
    )


@router.get("/kpgs/gate")
def get_kpgs_activation_gate() -> dict:
    """Automated gate — 300 agents SHIP required before sovereign sim."""
    return check_kpgs_activation_gate(write_report=True)


@router.post("/kpgs/smoke-poc")
def post_kpgs_smoke_poc() -> dict:
    """Full KPGS smoke PoC: gate → governance → steward → behavioral → sim → receipt."""
    return run_kpgs_smoke_poc()


@router.get("/kpgs/behavioral-poc")
def get_kpgs_behavioral_poc() -> dict:
    """Mechanical KPGS proofs — hood dispatch, context bleed, sim tick."""
    return run_kpgs_behavioral_poc(write_report=True)


@router.post("/sovereign-sim/tick")
def post_sovereign_sim_tick(body: dict | None = None) -> dict:
    """One sovereign sim game tick — sample hood agents, GUI-token dispatch."""
    sample = 12
    if body and body.get("sample_size"):
        sample = int(body["sample_size"])
    return run_sovereign_sim_tick(sample_size=sample, write_world=True)


@router.get("/sovereign-sim/status")
def get_sovereign_sim_status() -> dict:
    return sovereign_sim_status()


@router.get("/sovereign-sim/ui")
def get_sovereign_sim_ui() -> dict:
    """GUI snapshot — KC · Cassy · Kopano Context + world regions."""
    return sovereign_sim_ui_snapshot()


@router.post("/sovereign-sim/bootstrap")
def post_sovereign_sim_bootstrap() -> dict:
    return bootstrap_sovereign_sim()


@router.get("/boot/v1/promotion-check/{agent_id}")
def get_promotion_check(agent_id: str) -> dict:
    return promotion_allowed(agent_id)


@router.post("/poc/validate")
def post_poc_validate(body: EcoPocValidateBody) -> dict:
    """Validate PoC with Rosen (M,R) + measurable Δ + livelihood signals."""
    return validate_eco_poc(
        agent_id=body.agent_id,
        claim=body.claim,
        model=body.model,
        relation=body.relation,
        baseline=body.baseline,
        observed=body.observed,
        unit=body.unit,
        instrument=body.instrument,
        evidence=body.evidence,
        exit_code=body.exit_code,
        livelihood_ids=body.livelihood_ids or None,
        anticipated_delta=body.anticipated_delta,
    )


@router.post("/populate-main-brain")
def post_populate(
    body: PhuPopulateBody,
    operator: dict = Depends(_require_god),
) -> dict:
    """
    Populate Main Brain from Schematics: sync logs, reattach sub-brains,
    append Bracket Protocol receipt.
    """
    try:
        result = populate_main_brain(sync_vault_logs=body.sync_vault_logs)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"operator": operator["email"], **result}
