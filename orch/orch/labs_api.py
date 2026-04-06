from __future__ import annotations

from fastapi import APIRouter

from .labs_registry import get_labs_overview
from .launch_config import get_launch_surface_config
from .sa_access import build_access_plan


router = APIRouter(prefix="/api/labs", tags=["labs"])


@router.get("/overview")
def labs_overview() -> dict:
    return get_labs_overview()


@router.get("/tools")
def labs_tools() -> dict:
    return {"tools": get_labs_overview()["tools"]}


@router.get("/categories")
def labs_categories() -> dict:
    return {"categories": get_labs_overview()["categories"]}


@router.get("/phases")
def labs_phases() -> dict:
    return {"phases": get_labs_overview()["phases"]}


@router.get("/languages")
def labs_languages() -> dict:
    overview = get_labs_overview()
    return {
        "languages": overview["languages"],
        "access_modes": overview["access_modes"],
    }


@router.get("/cowork")
def labs_cowork() -> dict:
    overview = get_labs_overview()
    return {
        "cowork_surfaces": overview["cowork_surfaces"],
        "orch_code_tracks": overview["orch_code_tracks"],
    }


@router.get("/language-plan")
def labs_language_plan(
    preferred_language: str | None = None,
    preferred_input: str | None = None,
    speech_impairment: bool = False,
) -> dict:
    return build_access_plan(
        preferred_language=preferred_language,
        preferred_input=preferred_input,
        speech_impairment=speech_impairment,
    )


@router.get("/launch-config")
def labs_launch_config() -> dict:
    return get_launch_surface_config()
