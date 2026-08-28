"""Kopano runtime package bootstrap."""

from .department_contract_aliases import install_legacy_department_aliases

# Transitional compatibility: persisted TSAP department ids are mapped onto
# existing frozen v2 contracts before Guardian/Identi flows execute.  This does
# not add authority; it ensures legacy state is governed instead of falsely
# failing as UNKNOWN_DEPARTMENT.
install_legacy_department_aliases()

# KPCB+ governed analytical projections. These operators expose GROUP/PIVOT/
# ATTENTION semantics over protocol/context records while preserving source
# testimony and refusing to infer authority/action permission from aggregates.
from .kpcb_analytics import KPCBAnalyticalCorpus, KPCBAnalyticsError  # noqa: E402,F401
