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

# 24-RTC Learning Suite Implementations:
from .fep_engine import ForensicEvolutionProtocolEngine, EvidenceClass  # noqa: E402,F401
from .reality_to_cloud_workflow import RealityToCloudWorkflowOrchestrator, WorkflowStage  # noqa: E402,F401
from .mmao_mao_identity_mesh import MmaoMaoIdentityRecycler, DeviceOperatingMode  # noqa: E402,F401
from .possibility_to_proof_engine import PossibilityToProofEngine, BracketContainerType  # noqa: E402,F401
from .canonical_data_governance_orchestrator import CanonicalDataGovernanceOrchestrator  # noqa: E402,F401
