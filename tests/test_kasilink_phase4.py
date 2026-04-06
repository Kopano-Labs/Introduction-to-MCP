from fastapi.testclient import TestClient

from orch.orch.api import app
from orch.orch.tools.gig_matcher import match_gig
from orch.orch.tools.loadshedding import get_loadshedding_status, is_gig_safe


client = TestClient(app)


def test_match_gig_returns_ranked_summary():
    result = match_gig(
        description="Need an electrician for urgent wiring repair",
        location="Soweto",
        category="repairs",
        skills=["electrical", "wiring"],
        providers=[
            {
                "id": "nearby-pro",
                "skills": ["electrical", "wiring"],
                "verified": True,
                "distance_km": 2,
                "reliability": 0.9,
                "available": True,
                "category": "repairs",
            },
            {
                "id": "farther-pro",
                "skills": ["electrical"],
                "verified": False,
                "distance_km": 12,
                "reliability": 0.5,
                "available": True,
                "category": "repairs",
            },
        ],
    )

    assert result["summary"]["recommended_provider_id"] == "nearby-pro"
    assert result["summary"]["shortlisted"] == 2
    assert result["matches"][0]["score"] >= result["matches"][1]["score"]
    assert "score_breakdown" in result["matches"][0]


def test_loadshedding_status_has_current_shape():
    status = get_loadshedding_status("soweto-zone-1")
    assert status["area_id"] == "soweto-zone-1"
    assert "windows" in status
    assert "active_now" in status
    assert "updated_at" in status


def test_is_gig_safe_detects_conflict():
    status = get_loadshedding_status("soweto-zone-1")
    first_window = status["windows"][0]
    result = is_gig_safe("soweto-zone-1", first_window["start"], duration_hours=1.0)
    assert result["safe"] is False
    assert result["conflicting_windows"]


def test_kasilink_health_and_dashboard_routes():
    health = client.get("/api/kasilink/health")
    assert health.status_code == 200
    assert "moderate" in health.json()["features"]

    dashboard = client.get("/api/kasilink/dashboard")
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["status"] == "ready"
    assert "metrics" in payload


def test_kasilink_moderation_route():
    response = client.post("/api/kasilink/moderate", json={"text": "This looks like a scam listing"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["approved"] is False
    assert "scam" in payload["matched_terms"]


def test_kasilink_forecast_route():
    response = client.post(
        "/api/kasilink/forecast",
        json={"category": "delivery", "area": "alexandra", "horizon_days": 5, "recent_demand": [3, 4, 5, 6]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["category"] == "delivery"
    assert payload["area"] == "alexandra"
    assert payload["predicted_jobs"] > 0
