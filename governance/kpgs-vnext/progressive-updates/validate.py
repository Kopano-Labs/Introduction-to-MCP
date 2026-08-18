"""Dependency-free structural validator for the APU -> CRUD -> SWFUS contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / "kopano-core" / "kopano" / "swfus_engine.py"
KESSA = ROOT / "kopano-core" / "kopano" / "kessa_mmao_api.py"
SCHEMA = Path(__file__).with_name("progressive-update.schema.json")
README = Path(__file__).with_name("README.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-SWFUS FAIL: {message}")


def load_runtime():
    spec = importlib.util.spec_from_file_location("kpgs_swfus_contract", RUNTIME)
    require(spec is not None and spec.loader is not None, "runtime module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    docs = README.read_text(encoding="utf-8")
    runtime_source = RUNTIME.read_text(encoding="utf-8")
    kessa_source = KESSA.read_text(encoding="utf-8")

    require(schema["properties"]["boundary_marker"]["const"] == "#NB", "#NB marker drifted")
    require(
        schema["properties"]["authority_effect"]["const"] == "none",
        "progressive update schema widened authority",
    )
    require(
        "constitutional_truth" not in schema["properties"]["state_class"]["enum"],
        "authoritative state entered SWFUS schema",
    )

    expected_order = [
        "TELEMETRY",
        "CLASSIFICATION",
        "ROUTING",
        "PROTOCOL_SELECTION",
        "INVARIANT_AUDIT",
        "POC_FOC_CHECK",
        "STATE_UPDATE",
        "DISTRIBUTION",
    ]
    runtime = load_runtime()
    require(list(runtime.SWFUS_STAGE_ORDER) == expected_order, "canonical stage ordering changed")
    require(
        runtime.SWFUS_CANONICAL_NAME == "State-Wide Framework Universal Synchronization",
        "canonical SWFUS name drifted",
    )

    engine = runtime.SwfusHierarchy()
    receipt = engine.execute_update(
        runtime.ProgressiveUpdate(
            update_id="validator-001",
            node_id="validator-node",
            operation=runtime.CrudOperation.CREATE,
            lane="validation",
            context_route="kpgs-vnext.progressive-updates",
            protocol="APU->CRUD->SWFUS",
            idempotency_key="validator-idem-001",
            value={"status": "green"},
            apu_status="GREEN",
            poc_validated=True,
            evidence_refs=("validator://structural-proof",),
            boundary_marker="#NB",
        )
    )
    require(receipt.disposition == "APPLIED", "valid progressive update did not apply")
    require(receipt.synchronized, "valid progressive update did not distribute")
    require(not receipt.canonical_authority_changed, "synchronization changed canonical authority")
    require(len(engine.distribution_log) == 1, "distribution receipt missing")
    require(
        engine.distribution_log[0]["transport_grants_authority"] is False,
        "transport gained authority",
    )

    blocked = engine.execute_update(
        runtime.ProgressiveUpdate(
            update_id="validator-red",
            node_id="blocked-node",
            operation=runtime.CrudOperation.CREATE,
            lane="validation",
            context_route="kpgs-vnext.progressive-updates",
            protocol="APU->CRUD->SWFUS",
            idempotency_key="validator-idem-red",
            value={"status": "red"},
            apu_status="RED",
            poc_validated=True,
            evidence_refs=("validator://must-still-block",),
            boundary_marker="#NB",
        )
    )
    require(blocked.disposition == "REJECTED", "APU RED escaped governance")
    require("blocked-node" not in engine.projection_store, "rejected update mutated projection")

    require("SYNC_AZURE" not in kessa_source, "legacy provider-specific sync claim remains")
    require("azure_sync_id=\"6962519\"" not in runtime_source, "hard-coded Azure sync authority remains")
    require("Synchronization is not authority" in runtime_source, "authority boundary missing")
    require("Availability and synchronization are not authority" in docs, "offline authority law missing")
    require("#NB" in docs and "does **not** invent an expansion" in docs, "#NB boundary not preserved")

    print(
        "KPGS-SWFUS PASS: APU -> Progressive Update -> #NB -> CRUD -> "
        "State-Wide Framework Universal Synchronization is fail-closed and non-authoritative."
    )


if __name__ == "__main__":
    main()
