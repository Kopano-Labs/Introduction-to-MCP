from __future__ import annotations

from typing import Any, Dict, List


def _score_provider(provider: Dict[str, Any], gig: Dict[str, Any]) -> float:
    score = 0.0
    skills = {s.lower() for s in provider.get("skills", [])}
    required = {s.lower() for s in gig.get("skills", [])}
    score += 3.0 * len(skills & required)
    if provider.get("verified"):
        score += 1.5
    distance = provider.get("distance_km")
    if distance is not None:
        score += max(0.0, 2.0 - float(distance) / 5.0)
    reliability = provider.get("reliability", 0.0)
    score += float(reliability)
    availability = provider.get("available", True)
    if not availability:
        score -= 3.0
    return round(score, 3)


def match_gig(description: str, location: str, category: str, skills: List[str], providers: List[Dict[str, Any]]) -> Dict[str, Any]:
    gig = {
        "description": description,
        "location": location,
        "category": category,
        "skills": skills,
    }
    ranked = rank_providers(providers, gig)
    return {"gig": gig, "matches": ranked[:5]}


def rank_providers(providers: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    ranked = []
    for provider in providers:
        entry = dict(provider)
        entry["score"] = _score_provider(provider, criteria)
        ranked.append(entry)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
