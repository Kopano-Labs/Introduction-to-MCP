"""Super God Mode API — monorepo control for the whole Studio PWA (Cassy-forward)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .monorepo_control import (
    capabilities_payload,
    execute_git_action,
    execute_script_action,
    git_snapshot,
)
from .operator_auth import load_persisted_desktop_session, require_operator

router = APIRouter(prefix="/api/kc/god", tags=["kc-god-mode"])


class GodActionBody(BaseModel):
    action: str
    confirm: bool = Field(default=False)


def _require_god(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    return require_operator(authorization, god_only=True)


@router.get("/capabilities")
def god_capabilities() -> dict:
    return capabilities_payload()


@router.get("/me")
def god_me(operator: dict = Depends(_require_god)) -> dict:
    return {
        "user": operator,
        "super_god_mode": True,
        "scope": "whole_pwa_monorepo",
        "lead_student": "cassy",
        "teacher": "cassey",
        "brain": "kc",
    }


@router.get("/overview")
def god_overview(operator: dict = Depends(_require_god)) -> dict:
    from .kc_swarm_console_api import gather_status

    status = gather_status()
    return {
        "schema": "kc_god_overview_v1",
        "operator": operator["email"],
        "capabilities": capabilities_payload(),
        "git": git_snapshot(),
        "swarm_console": status,
        "cassy": status.get("cassy"),
        "persona_route": status.get("persona_route"),
        "proof_bar_pass": status.get("proof_bar_pass"),
    }


@router.get("/desktop-session")
def god_desktop_session(request: Request) -> dict:
    client_host = request.client.host if request.client else ""
    if client_host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail="Desktop session is localhost-only.")
    data = load_persisted_desktop_session()
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No operator session. Run scripts/kc_setup_operator.ps1 then restart the API.",
        )
    return data


@router.post("/actions/run")
def god_run_action(body: GodActionBody, operator: dict = Depends(_require_god)) -> dict:
    try:
        result = execute_script_action(body.action, confirm=body.confirm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    from .kc_swarm_console_api import gather_status

    return {
        **result,
        "operator": operator["email"],
        "swarm_console": gather_status(),
    }


@router.post("/git/run")
def god_run_git(body: GodActionBody, operator: dict = Depends(_require_god)) -> dict:
    try:
        result = execute_git_action(body.action, confirm=body.confirm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {**result, "operator": operator["email"]}
