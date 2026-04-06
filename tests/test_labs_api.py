from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from orch.orch import database
from orch.orch.api import app


client = TestClient(app)


@pytest.fixture
def isolated_labs_db(tmp_path, monkeypatch):
    db_path = tmp_path / "labs_test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db()
    yield db_path


def test_labs_overview_endpoint():
    response = client.get("/api/labs/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Orch Labs"
    assert payload["metrics"]["tools"] >= 1


def test_labs_tools_include_sa_access_items():
    response = client.get("/api/labs/tools")
    assert response.status_code == 200
    ids = {tool["id"] for tool in response.json()["tools"]}
    assert "sa-language-engine" in ids
    assert "speech-access-assistant" in ids


def test_labs_languages_include_sasl_and_access_modes():
    response = client.get("/api/labs/languages")
    assert response.status_code == 200
    payload = response.json()
    language_ids = {language["id"] for language in payload["languages"]}
    access_ids = {mode["id"] for mode in payload["access_modes"]}
    assert "sasl-za" in language_ids
    assert "aac" in access_ids


def test_labs_cowork_exposes_orch_code():
    response = client.get("/api/labs/cowork")
    assert response.status_code == 200
    payload = response.json()
    surface_ids = {surface["id"] for surface in payload["cowork_surfaces"]}
    track_ids = {track["id"] for track in payload["orch_code_tracks"]}
    assert "orch-code" in surface_ids
    assert "product-craft" in track_ids


def test_labs_language_plan_prioritizes_accessibility():
    response = client.get(
        "/api/labs/language-plan",
        params={"preferred_language": "isiZulu", "speech_impairment": "true"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"]["name"] == "isiZulu"
    assert payload["recommended_mode"]["id"] == "aac"


def test_labs_launch_config_exposes_anthropic_codex_mix():
    response = client.get("/api/labs/launch-config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["visual_mix"]["anthropic"] == 0.5
    assert payload["visual_mix"]["codex"] == 0.5
    assert payload["cowork"]["stitch_canvas"] is True


def test_translate_endpoint_uses_phrasebook():
    response = client.post(
        "/api/labs/translate",
        json={"text": "acknowledged", "target_language": "isiZulu"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["translated_text"] == "Kuqinisekisiwe"
    assert payload["target_language"]["id"] == "zu-za"


def test_route_prompt_detects_language():
    response = client.post(
        "/api/labs/route-prompt",
        json={"prompt": "Sawubona, ngicela usizo", "target_language": "English"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language_id"] == "zu-za"
    assert payload["response_language_id"] == "en-za"
    assert payload["translation_required"] is True


def test_multilingual_response_adds_glossary():
    response = client.post(
        "/api/labs/multilingual-response",
        json={"text": "next step: confirm booking", "preferred_language": "isiZulu", "domain": "jobs"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["response_labels"]["next_step"] == "Isinyathelo esilandelayo"
    assert any(term["source"] == "booking" for term in payload["glossary_terms"])


def test_access_execute_requires_confirmation_for_speech_impairment():
    response = client.post(
        "/api/labs/access/execute",
        json={
            "message": "job tomorrow",
            "preferred_language": "English",
            "preferred_input": "voice",
            "speech_impairment": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_mode"]["id"] == "aac"
    assert payload["requires_confirmation"] is True


def test_cowork_room_flow_persists_tasks(isolated_labs_db):
    create_response = client.post(
        "/api/labs/cowork/rooms",
        json={"name": "Phase 8 Build Room", "mission": "Ship the first cowork flow", "lead": "Lead"},
    )
    assert create_response.status_code == 200
    room = create_response.json()["room"]
    assert room["name"] == "Phase 8 Build Room"
    assert len(room["tasks"]) == 3

    task_response = client.post(
        f"/api/labs/cowork/rooms/{room['id']}/tasks",
        json={
            "title": "Implement room timeline",
            "description": "Add timeline and dispatch actions.",
            "owner": "DEV_1",
            "priority": "critical",
            "lane": "build",
        },
    )
    assert task_response.status_code == 200
    task = task_response.json()["task"]
    assert task["owner"] == "DEV_1"

    update_response = client.post(
        f"/api/labs/cowork/tasks/{task['id']}/status",
        json={"status": "in_progress"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["task"]["status"] == "in_progress"

    detail_response = client.get(f"/api/labs/cowork/rooms/{room['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()["room"]
    assert any(item["title"] == "Implement room timeline" for item in detail["lanes"]["build"])
    assert detail["dispatch_summary"]["in_progress"] >= 1


def test_cowork_task_can_be_reassigned(isolated_labs_db):
    create_response = client.post(
        "/api/labs/cowork/rooms",
        json={"name": "Dispatch Room", "mission": "Route tasks clearly", "lead": "Lead"},
    )
    room = create_response.json()["room"]
    task_id = room["tasks"][0]["id"]

    assign_response = client.post(
        f"/api/labs/cowork/tasks/{task_id}/owner",
        json={"owner": "DEV_2"},
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["task"]["owner"] == "DEV_2"


def test_orch_code_teaching_loop_reads_repo_patterns(isolated_labs_db):
    teach_response = client.post("/api/labs/orch-code/teach")
    assert teach_response.status_code == 200
    payload = teach_response.json()
    lesson_keys = {lesson["lesson_key"] for lesson in payload["taught_lessons"]}
    assert "python-fastapi-api" in lesson_keys
    assert "schematics-discipline" in lesson_keys

    profile_response = client.get("/api/labs/orch-code/profile")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["title"] == "Orch Code"
    assert profile["summary"]["learned_lessons"] >= 1
    assert "python-core" in profile["tracks"]


def test_orch_code_lesson_status_can_advance(isolated_labs_db):
    client.post("/api/labs/orch-code/teach")
    update_response = client.post(
        "/api/labs/orch-code/lessons/python-fastapi-api/status",
        json={"status": "learning", "confidence": 91},
    )
    assert update_response.status_code == 200
    lesson = update_response.json()["lesson"]
    assert lesson["status"] == "learning"
    assert lesson["confidence"] == 91


def test_mcp_console_chat_routes_cli_queries():
    response = client.post(
        "/api/labs/mcp-console/chat",
        json={"message": "How do I use the CLI and terminal flow for Orch?"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["topic"] == "cli"
    assert "CLI" in payload["surfaces"]
