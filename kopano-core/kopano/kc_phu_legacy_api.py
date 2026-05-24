"""Kopano-Phu legacy API — Cassy under Kopano Labs + Ama-Phu; Bracket Protocol."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from .operator_auth import require_operator
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
