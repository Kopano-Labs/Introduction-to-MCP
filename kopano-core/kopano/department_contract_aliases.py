"""Compatibility bridge between legacy TSAP department ids and v2 contracts.

The TSAP runtime predates the DEPT-* contract registry.  The legacy ids remain
part of persisted TSAP state and public tool inputs, while the v2 LPH/LPM gate
requires a current DepartmentContract.  These aliases point at existing frozen
contracts; they do not create new authority or weaken any boundary.
"""

from __future__ import annotations

from .department_contracts import CONTRACTS


LEGACY_TSAP_CONTRACT_ALIASES: dict[str, str] = {
    # Kopano Labs experimentation hosts the current AI/agent-validation lane.
    "kopano_labs_experimentation": "DEPT-AI",
    # AMA-PHU creativity is product/experience work in the current contract set.
    "ama_phu_creativity": "DEPT-PRODUCT",
}


def install_legacy_department_aliases() -> tuple[str, ...]:
    """Install explicit aliases without replacing canonical DEPT-* contracts."""
    installed: list[str] = []
    for legacy_id, canonical_id in LEGACY_TSAP_CONTRACT_ALIASES.items():
        canonical = CONTRACTS.get(canonical_id)
        if canonical is None:
            raise RuntimeError(
                f"Cannot install TSAP alias {legacy_id!r}: missing canonical contract {canonical_id!r}"
            )
        existing = CONTRACTS.get(legacy_id)
        if existing is not None and existing is not canonical:
            raise RuntimeError(
                f"Refusing to overwrite existing department contract for legacy id {legacy_id!r}"
            )
        CONTRACTS[legacy_id] = canonical
        installed.append(legacy_id)
    return tuple(installed)
