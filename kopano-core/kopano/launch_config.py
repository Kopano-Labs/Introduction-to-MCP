from __future__ import annotations

from typing import Any


def get_launch_surface_config() -> dict[str, Any]:
    return {
        "surface": "cassy_labs_launch",
        "visual_mix": {
            "anthropic": 0.5,
            "codex": 0.5,
            "notes": [
                "artifact-style workspace cards",
                "command-center task rails",
                "clean text hierarchy with strong review affordances",
            ],
        },
        "cowork": {
            "enabled": True,
            "stitch_canvas": True,
            "modes": ["cassy-forge", "cassy-code"],
        },
        "launch_sections": [
            "labs hero",
            "tool catalog",
            "sa language coverage",
            "accessibility modes",
            "cowork surfaces",
            "Cassy code teaching tracks",
        ],
    }
 
