from __future__ import annotations

from fastapi import APIRouter

from .labs_registry import get_labs_overview


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
