from __future__ import annotations

from typing import Any

from .labs_registry import ACCESS_MODES, SA_LANGUAGE_SUPPORT


LANGUAGE_INDEX = {entry["id"]: entry for entry in SA_LANGUAGE_SUPPORT}
LANGUAGE_NAME_INDEX = {entry["name"].lower(): entry for entry in SA_LANGUAGE_SUPPORT}


def resolve_language_support(preferred_language: str | None = None) -> dict[str, Any]:
    if not preferred_language:
        selected = LANGUAGE_INDEX["en-za"]
    else:
        key = preferred_language.strip().lower()
        selected = LANGUAGE_INDEX.get(key) or LANGUAGE_NAME_INDEX.get(key) or LANGUAGE_INDEX["en-za"]

    return {
        "selected_language": selected,
        "supported_languages": SA_LANGUAGE_SUPPORT,
        "coverage_summary": {
            "official_languages": len(SA_LANGUAGE_SUPPORT),
            "includes_sign_language": any(language["id"] == "sasl-za" for language in SA_LANGUAGE_SUPPORT),
        },
    }


def build_access_plan(
    preferred_language: str | None = None,
    preferred_input: str | None = None,
    speech_impairment: bool = False,
) -> dict[str, Any]:
    language_support = resolve_language_support(preferred_language)
    access_modes = ACCESS_MODES

    recommended_mode = "voice-text"
    if speech_impairment:
        recommended_mode = "aac"
    elif preferred_input in {"text", "keyboard"}:
        recommended_mode = "text-first"
    elif preferred_input in {"aac", "assistive"}:
        recommended_mode = "aac"

    return {
        "language": language_support["selected_language"],
        "recommended_mode": next(mode for mode in access_modes if mode["id"] == recommended_mode),
        "available_modes": access_modes,
        "speech_impairment_aware": speech_impairment,
        "design_rules": [
            "confirm intent before action when confidence is low",
            "keep a full text-first path for every voice flow",
            "support AAC shortcuts for repeated intents",
            "never assume English when a local language is provided",
        ],
    }
