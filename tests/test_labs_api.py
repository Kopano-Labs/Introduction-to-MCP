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
