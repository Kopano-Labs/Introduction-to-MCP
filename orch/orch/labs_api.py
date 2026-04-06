from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .cowork import add_cowork_task, create_cowork_room, get_cowork_room, list_cowork_rooms, update_cowork_task
from .labs_registry import get_labs_overview
from .language_runtime import route_multilingual_prompt, translate_text
from .launch_config import get_launch_surface_config
from .orch_code import get_orch_code_profile, teach_repo_patterns
from .sa_access import build_access_plan


router = APIRouter(prefix="/api/labs", tags=["labs"])


class TranslationRequest(BaseModel):
    text: str
    target_language: str
    domain: str = "general"


class RoutePromptRequest(BaseModel):
    prompt: str
    preferred_language: str | None = None
    target_language: str | None = None


class CoworkRoomRequest(BaseModel):
    name: str
    mission: str
    lead: str = "Lead"


class CoworkTaskRequest(BaseModel):
    title: str
    description: str
    owner: str
    priority: str = "high"
    lane: str = "build"


class CoworkTaskStatusRequest(BaseModel):
    status: str


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


@router.post("/translate")
def labs_translate(request: TranslationRequest) -> dict:
    return translate_text(request.text, request.target_language, domain=request.domain)


@router.post("/route-prompt")
def labs_route_prompt(request: RoutePromptRequest) -> dict:
    return route_multilingual_prompt(
        request.prompt,
        preferred_language=request.preferred_language,
        target_language=request.target_language,
    )


@router.get("/cowork/rooms")
def cowork_rooms() -> dict:
    return {"rooms": list_cowork_rooms()}


@router.post("/cowork/rooms")
def cowork_create_room(request: CoworkRoomRequest) -> dict:
    return {"room": create_cowork_room(request.name, request.mission, lead=request.lead)}


@router.get("/cowork/rooms/{room_id}")
def cowork_room_detail(room_id: int) -> dict:
    return {"room": get_cowork_room(room_id)}


@router.post("/cowork/rooms/{room_id}/tasks")
def cowork_create_task(room_id: int, request: CoworkTaskRequest) -> dict:
    return {
        "task": add_cowork_task(
            room_id,
            request.title,
            request.description,
            request.owner,
            priority=request.priority,
            lane=request.lane,
        )
    }


@router.post("/cowork/tasks/{task_id}/status")
def cowork_update_task_status(task_id: int, request: CoworkTaskStatusRequest) -> dict:
    return {"task": update_cowork_task(task_id, request.status)}


@router.post("/orch-code/teach")
def orch_code_teach() -> dict:
    return teach_repo_patterns()


@router.get("/orch-code/profile")
def orch_code_profile() -> dict:
    return get_orch_code_profile()
