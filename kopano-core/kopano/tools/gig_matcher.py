from __future__ import annotations

from typing import Any, Dict, List


def _score_breakdown(provider: Dict[str, Any], gig: Dict[str, Any]) -> Dict[str, float]:
    breakdown = {
        "skills": 0.0,
        "verification": 0.0,
        "distance": 0.0,
        "reliability": 0.0,
        "availability": 0.0,
        "category": 0.0,
    }
    skills = {s.lower() for s in provider.get("skills", [])}
    required = {s.lower() for s in gig.get("skills", [])}
    breakdown["skills"] = 3.0 * len(skills & required)
    if provider.get("verified"):
        breakdown["verification"] = 1.5
    distance = provider.get("distance_km")
    if distance is not None:
        breakdown["distance"] = max(0.0, 2.0 - float(distance) / 5.0)
    reliability = provider.get("reliability", 0.0)
    breakdown["reliability"] = float(reliability)
    availability = provider.get("available", True)
    if not availability:
        breakdown["availability"] = -3.0
    provider_category = str(provider.get("category", "")).strip().lower()
    gig_category = str(gig.get("category", "")).strip().lower()
    if provider_category and gig_category and provider_category == gig_category:
        breakdown["category"] = 1.25
    return {key: round(value, 3) for key, value in breakdown.items()}


def _score_provider(provider: Dict[str, Any], gig: Dict[str, Any]) -> float:
    breakdown = _score_breakdown(provider, gig)
    return round(sum(breakdown.values()), 3)


def _match_summary(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not matches:
        return {
            "recommended_provider_id": None,
            "average_score": 0.0,
            "verified_match_count": 0,
        }
    return {
        "recommended_provider_id": matches[0].get("id") or matches[0].get("provider_id") or matches[0].get("name"),
        "average_score": round(sum(match["score"] for match in matches) / len(matches), 3),
        "verified_match_count": sum(1 for match in matches if match.get("verified")),
    }


def match_gig(description: str, location: str, category: str, skills: List[str], providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    gig = {
        "description": description,
        "location": location,
        "category": category,
        "skills": skills,
    }
    ranked = rank_providers(providers, gig)
    top_matches = ranked[:5]
    return {
        "gig": gig,
        "matches": top_matches,
        "summary": {
            **_match_summary(top_matches),
            "total_candidates": len(providers),
            "shortlisted": len(top_matches),
        },
    }


def rank_providers(providers: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    ranked = []
    for provider in providers:
        entry = dict(provider)
        entry["score_breakdown"] = _score_breakdown(provider, criteria)
        entry["score"] = _score_provider(provider, criteria)
        ranked.append(entry)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
