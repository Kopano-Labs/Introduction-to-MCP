from fastapi.testclient import TestClient

from orch.orch.api import app


client = TestClient(app)


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
