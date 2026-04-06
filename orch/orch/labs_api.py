from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .cowork import (
    add_cowork_task,
    add_cowork_artifact,
    create_cowork_room,
    get_creator_analytics,
    get_cowork_room,
    list_cowork_rooms,
    move_cowork_task,
    reassign_cowork_task,
    update_cowork_task,
)
from .labs_registry import get_labs_overview
from .language_runtime import build_multilingual_response, route_multilingual_prompt, translate_text
from .launch_config import get_launch_surface_config
from .mcp_console import answer_mcp_console, get_console_analytics
from .orch_code import get_orch_code_controls, get_orch_code_profile, teach_repo_patterns, update_lesson_status
from .sa_access import build_access_plan, execute_access_session


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


class CoworkTaskOwnerRequest(BaseModel):
    owner: str


class CoworkTaskLaneRequest(BaseModel):
    lane: str


class CoworkArtifactRequest(BaseModel):
    artifact_type: str
    title: str
    summary: str
    status: str = "draft"
    link: str | None = None


class MultilingualResponseRequest(BaseModel):
    text: str
    preferred_language: str | None = None
    domain: str = "general"
    include_glossary: bool = True


class AccessExecutionRequest(BaseModel):
    message: str
    preferred_language: str | None = None
    preferred_input: str | None = None
    speech_impairment: bool = False


class LessonStatusRequest(BaseModel):
    status: str
    confidence: int | None = None


class McpConsoleRequest(BaseModel):
    message: str
    session_id: int | None = None


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


@router.post("/multilingual-response")
def labs_multilingual_response(request: MultilingualResponseRequest) -> dict:
    return build_multilingual_response(
        request.text,
        preferred_language=request.preferred_language,
        domain=request.domain,
        include_glossary=request.include_glossary,
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


@router.post("/cowork/tasks/{task_id}/owner")
def cowork_update_task_owner(task_id: int, request: CoworkTaskOwnerRequest) -> dict:
    return {"task": reassign_cowork_task(task_id, request.owner)}


@router.post("/cowork/tasks/{task_id}/lane")
def cowork_update_task_lane(task_id: int, request: CoworkTaskLaneRequest) -> dict:
    return {"task": move_cowork_task(task_id, request.lane)}


@router.post("/cowork/rooms/{room_id}/artifacts")
def cowork_create_artifact(room_id: int, request: CoworkArtifactRequest) -> dict:
    return {
        "artifact": add_cowork_artifact(
            room_id,
            request.artifact_type,
            request.title,
            request.summary,
            status=request.status,
            link=request.link,
        )
    }


@router.get("/analytics")
def labs_analytics() -> dict:
    return {
        "forge": get_creator_analytics(),
        "mcp_console": get_console_analytics(),
    }


@router.post("/orch-code/teach")
def orch_code_teach() -> dict:
    return teach_repo_patterns()


@router.get("/orch-code/profile")
def orch_code_profile() -> dict:
    return get_orch_code_profile()


@router.get("/orch-code/controls")
def orch_code_controls() -> dict:
    return get_orch_code_controls()


@router.post("/orch-code/lessons/{lesson_key}/status")
def orch_code_update_status(lesson_key: str, request: LessonStatusRequest) -> dict:
    return {"lesson": update_lesson_status(lesson_key, request.status, confidence=request.confidence)}


@router.post("/access/execute")
def labs_access_execute(request: AccessExecutionRequest) -> dict:
    return execute_access_session(
        message=request.message,
        preferred_language=request.preferred_language,
        preferred_input=request.preferred_input,
        speech_impairment=request.speech_impairment,
    )


@router.post("/mcp-console/chat")
def labs_mcp_console_chat(request: McpConsoleRequest) -> dict:
    return answer_mcp_console(request.message, session_id=request.session_id)
