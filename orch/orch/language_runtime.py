from __future__ import annotations

from typing import Any

from .labs_registry import SA_LANGUAGE_SUPPORT


LANGUAGE_BY_ID = {entry["id"]: entry for entry in SA_LANGUAGE_SUPPORT}
LANGUAGE_BY_NAME = {entry["name"].lower(): entry for entry in SA_LANGUAGE_SUPPORT}

LANGUAGE_HINTS = {
    "sawubona": "zu-za",
    "unjani": "zu-za",
    "molo": "xh-za",
    "molweni": "xh-za",
    "dumela": "tn-za",
    "avuxeni": "ts-za",
    "ndaa": "ve-za",
    "goeie": "af-za",
}

PHRASEBOOK = {
    "acknowledged": {
        "en-za": "Acknowledged",
        "af-za": "Bevestig",
        "zu-za": "Kuqinisekisiwe",
        "xh-za": "Kuqinisekisiwe",
        "tn-za": "Go amogetswe",
        "st-za": "Ho amohetswe",
        "nso-za": "Go amogetswe",
        "ts-za": "Swi amukeriwile",
        "ve-za": "Zwo tanganedzwa",
        "nr-za": "Kwamukelwe",
        "ss-za": "Kwamukelwe",
        "sasl-za": "Acknowledged",
    },
    "next_step": {
        "en-za": "Next step",
        "af-za": "Volgende stap",
        "zu-za": "Isinyathelo esilandelayo",
        "xh-za": "Inyathelo elilandelayo",
        "tn-za": "Kgato e e latelang",
        "st-za": "Mohato o latelang",
        "nso-za": "Kgato ye e latelago",
        "ts-za": "Go landzela",
        "ve-za": "Vhukando vhu tevhelaho",
        "nr-za": "Isinyathelo esilandelako",
        "ss-za": "Sinyatselo lesilandzelako",
        "sasl-za": "Next step",
    },
}


def detect_language(text: str, preferred_language: str | None = None) -> dict[str, str]:
    if preferred_language:
        key = preferred_language.strip().lower()
        if key in LANGUAGE_BY_ID:
            return LANGUAGE_BY_ID[key]
        if key in LANGUAGE_BY_NAME:
            return LANGUAGE_BY_NAME[key]

    lower_text = text.lower()
    for hint, language_id in LANGUAGE_HINTS.items():
        if hint in lower_text:
            return LANGUAGE_BY_ID[language_id]

    return LANGUAGE_BY_ID["en-za"]


def translate_text(text: str, target_language: str, domain: str = "general") -> dict[str, Any]:
    language = detect_language(text="", preferred_language=target_language)
    lower_text = text.strip().lower()

    translated = text
    if lower_text in PHRASEBOOK:
        translated = PHRASEBOOK[lower_text].get(language["id"], text)
    elif ":" in text:
        left, right = text.split(":", 1)
        left_key = left.strip().lower().replace(" ", "_")
        translated_left = PHRASEBOOK.get(left_key, {}).get(language["id"], left.strip())
        translated = f"{translated_left}: {right.strip()}"

    return {
        "source_text": text,
        "translated_text": translated,
        "target_language": language,
        "domain": domain,
        "mode": "phrasebook-plus-fallback",
    }


def route_multilingual_prompt(
    prompt: str,
    preferred_language: str | None = None,
    target_language: str | None = None,
) -> dict[str, Any]:
    source_language = detect_language(prompt, preferred_language=preferred_language)
    response_language = detect_language("", preferred_language=target_language or source_language["id"])
    prompt_envelope = {
        "language_id": source_language["id"],
        "language_name": source_language["name"],
        "response_language_id": response_language["id"],
        "translation_required": source_language["id"] != response_language["id"],
        "normalized_prompt": prompt.strip(),
    }
    return prompt_envelope
