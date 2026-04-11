from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import settings
from .telemetry import configure_server_telemetry, get_server_telemetry_status

REPO_ROOT = Path(__file__).resolve().parents[2]
ORCH_ROOT = Path(__file__).resolve().parents[1]
GUI_ROOT = ORCH_ROOT / "studio"


def _safe_value(value: str | None) -> bool:
    return bool(value and value.strip())


def _module_installed(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def _package_version(package_json_path: Path) -> str | None:
    if not package_json_path.exists():
        return None
    try:
        payload = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload.get("version")


def _run_command(*command: str) -> dict[str, Any]:
    command_path = shutil.which(command[0])
    if command_path is None:
        return {"installed": False, "path": None, "stdout": "", "stderr": "", "returncode": None}

    args = [command_path, *command[1:]]
    if command_path.lower().endswith((".bat", ".cmd")):
        args = ["cmd", "/c", command_path, *command[1:]]

    result = subprocess.run(args, capture_output=True, text=True, check=False)
    return {
        "installed": True,
        "path": command_path,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def _get_az_status() -> dict[str, Any]:
    result = _run_command("az", "version", "--output", "json")
    version = None
    if result["installed"] and result["returncode"] == 0 and result["stdout"]:
        try:
            payload = json.loads(result["stdout"])
            version = payload.get("azure-cli")
        except json.JSONDecodeError:
            version = None
    return {
        "installed": result["installed"],
        "version": version,
        "path": result["path"],
        "healthy": bool(result["installed"] and result["returncode"] == 0 and version),
        "error": result["stderr"] if result["returncode"] else "",
    }


def _get_azd_status() -> dict[str, Any]:
    result = _run_command("azd", "version")
    version = None
    if result["installed"] and result["returncode"] == 0 and result["stdout"]:
        version = result["stdout"].splitlines()[0].strip()
    return {
        "installed": result["installed"],
        "version": version,
        "path": result["path"],
        "healthy": bool(result["installed"] and result["returncode"] == 0 and version),
        "error": result["stderr"] if result["returncode"] else "",
    }


def _get_azure_account_status(az_status: dict[str, Any]) -> dict[str, Any]:
    if not az_status["installed"]:
        return {
            "logged_in": False,
            "subscription_name": None,
            "subscription_id": None,
            "tenant_id": None,
            "reason": "az_missing",
        }

    result = _run_command("az", "account", "show", "--output", "json")
    if result["returncode"] != 0 or not result["stdout"]:
        reason = result["stderr"] or "not_logged_in"
        return {
            "logged_in": False,
            "subscription_name": None,
            "subscription_id": None,
            "tenant_id": None,
            "reason": reason,
        }

    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {
            "logged_in": False,
            "subscription_name": None,
            "subscription_id": None,
            "tenant_id": None,
            "reason": "account_output_unparseable",
        }

    return {
        "logged_in": True,
        "subscription_name": payload.get("name"),
        "subscription_id": payload.get("id"),
        "tenant_id": payload.get("tenantId"),
        "reason": "ok",
    }


def _build_env_status() -> dict[str, Any]:
    hosting_target = settings.azure_container_app_name or settings.azure_app_service_name

    return {
        "azure_openai": {
            "configured": all(
                (
                    _safe_value(settings.azure_openai_endpoint),
                    _safe_value(settings.azure_openai_api_key),
                    _safe_value(settings.azure_openai_deployment),
                )
            ),
            "missing": [
                name
                for name, value in [
                    ("AZURE_OPENAI_ENDPOINT", settings.azure_openai_endpoint),
                    ("AZURE_OPENAI_API_KEY", settings.azure_openai_api_key),
                    ("AZURE_OPENAI_DEPLOYMENT", settings.azure_openai_deployment),
                ]
                if not _safe_value(value)
            ],
        },
        "app_insights": {
            "configured": _safe_value(settings.azure_app_insights_connection_string),
            "missing": []
            if _safe_value(settings.azure_app_insights_connection_string)
            else ["AZURE_APP_INSIGHTS_CONNECTION_STRING"],
        },
        "hosting": {
            "configured": all(
                (
                    _safe_value(settings.azure_subscription_id),
                    _safe_value(settings.azure_resource_group),
                    _safe_value(hosting_target),
                )
            ),
            "missing": [
                name
                for name, value in [
                    ("AZURE_SUBSCRIPTION_ID", settings.azure_subscription_id),
                    ("AZURE_RESOURCE_GROUP", settings.azure_resource_group),
                    (
                        "AZURE_APP_SERVICE_NAME or AZURE_CONTAINER_APP_NAME",
                        hosting_target,
                    ),
                ]
                if not _safe_value(value)
            ],
        },
        "azure_ai_search": {
            "configured": all(
                (
                    _safe_value(settings.azure_ai_search_endpoint),
                    _safe_value(settings.azure_ai_search_key),
                    _safe_value(settings.azure_ai_search_index_name),
                )
            ),
            "missing": [
                name
                for name, value in [
                    ("AZURE_AI_SEARCH_ENDPOINT", settings.azure_ai_search_endpoint),
                    ("AZURE_AI_SEARCH_KEY", settings.azure_ai_search_key),
                    ("AZURE_AI_SEARCH_INDEX_NAME", settings.azure_ai_search_index_name),
                ]
                if not _safe_value(value)
            ],
        },
        "managed_identity": {
            "configured": _safe_value(settings.azure_client_id),
            "missing": []
            if _safe_value(settings.azure_client_id)
            else ["AZURE_CLIENT_ID"],
        },
    }


def _build_frontend_status() -> dict[str, Any]:
    package_json_path = GUI_ROOT / "node_modules" / "@microsoft" / "applicationinsights-web" / "package.json"
    version = _package_version(package_json_path)
    return {
        "application_insights_web": {
            "installed": version is not None,
            "version": version,
        }
    }


def gather_microsoft_readiness() -> dict[str, Any]:
    telemetry_state = configure_server_telemetry()
    az_status = _get_az_status()
    azd_status = _get_azd_status()
    azure_account = _get_azure_account_status(az_status)
    env_status = _build_env_status()
    python_packages = {
        "azure_monitor_opentelemetry": _module_installed("azure.monitor.opentelemetry"),
        "azure_identity": _module_installed("azure.identity"),
    }

    required_checks = [
        az_status["healthy"],
        azd_status["healthy"],
        azure_account["logged_in"],
        env_status["azure_openai"]["configured"],
        env_status["app_insights"]["configured"],
        env_status["hosting"]["configured"],
    ]
    optional_checks = [
        env_status["azure_ai_search"]["configured"],
        env_status["managed_identity"]["configured"],
        _build_frontend_status()["application_insights_web"]["installed"],
    ]

    next_steps: list[str] = []
    if not az_status["healthy"]:
        next_steps.append("Confirm `az version` works in the demo shell.")
    if not azd_status["healthy"]:
        next_steps.append("Confirm `azd version` works in the demo shell.")
    if not azure_account["logged_in"]:
        next_steps.append("Run `az login` and choose the Demo Day subscription.")
        next_steps.append("Run `azd auth login` after Azure CLI sign-in is confirmed.")
    if not env_status["azure_openai"]["configured"]:
        next_steps.append("Add Azure OpenAI endpoint, key, and deployed model name to the env file.")
    if not env_status["app_insights"]["configured"]:
        next_steps.append("Create Application Insights and add its connection string to the env file.")
    if not env_status["hosting"]["configured"]:
        next_steps.append("Set the target resource group and App Service or Container Apps name.")
    if not env_status["azure_ai_search"]["configured"]:
        next_steps.append("Add Azure AI Search only if that feature will be claimed in the live demo.")

    commands: list[str] = ["az version", "azd version"]
    commands.append("az account show" if azure_account["logged_in"] else "az login")
    commands.append("azd auth login")

    return {
        "summary": {
            "required_ready": sum(1 for check in required_checks if check),
            "required_total": len(required_checks),
            "optional_ready": sum(1 for check in optional_checks if check),
            "optional_total": len(optional_checks),
            "demo_ready": all(required_checks),
        },
        "tooling": {
            "az": az_status,
            "azd": azd_status,
            "python_packages": python_packages,
            "telemetry": telemetry_state if telemetry_state["attempted"] else get_server_telemetry_status(),
        },
        "azure_account": azure_account,
        "env": env_status,
        "frontend": _build_frontend_status(),
        "commands": commands,
        "next_steps": next_steps,
    }
