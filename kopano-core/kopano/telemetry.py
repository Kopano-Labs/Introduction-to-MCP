from __future__ import annotations

import json
import logging
from typing import Any

from .config import settings

logger = logging.getLogger("kopano.telemetry")

_telemetry_state: dict[str, Any] = {
    "attempted": False,
    "configured": False,
    "reason": "not_started",
}


def configure_server_telemetry() -> dict[str, Any]:
    """Configure Azure Monitor / Application Insights when a connection string exists."""
    global _telemetry_state

    if _telemetry_state["attempted"]:
        return dict(_telemetry_state)

    connection_string = settings.azure_app_insights_connection_string
    if not connection_string:
        _telemetry_state = {
            "attempted": True,
            "configured": False,
            "reason": "missing_connection_string",
        }
        return dict(_telemetry_state)

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="kopano.telemetry",
            instrumentation_options={
                "fastapi": {"enabled": True},
                "requests": {"enabled": True},
                "logging": {"enabled": True},
            },
            enable_live_metrics=True,
        )
        _telemetry_state = {
            "attempted": True,
            "configured": True,
            "reason": "configured",
        }
        logger.info("Azure Monitor telemetry configured for kopano.")
    except Exception as exc:  # pragma: no cover - defensive path
        _telemetry_state = {
            "attempted": True,
            "configured": False,
            "reason": f"configuration_failed:{exc.__class__.__name__}",
        }
        logger.warning("Azure Monitor telemetry configuration failed: %s", exc)

    return dict(_telemetry_state)


def get_server_telemetry_status() -> dict[str, Any]:
    return dict(_telemetry_state)


def log_demo_event(event_name: str, **details: Any) -> None:
    """Emit structured logs that App Insights can capture once configured."""
    if details:
        logger.info("%s | %s", event_name, json.dumps(details, sort_keys=True, default=str))
        return
    logger.info("%s", event_name)
