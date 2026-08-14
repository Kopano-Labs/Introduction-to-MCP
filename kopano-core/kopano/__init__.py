"""Kopano runtime package bootstrap."""

from .department_contract_aliases import install_legacy_department_aliases

# Transitional compatibility: persisted TSAP department ids are mapped onto
# existing frozen v2 contracts before Guardian/Identi flows execute.  This does
# not add authority; it ensures legacy state is governed instead of falsely
# failing as UNKNOWN_DEPARTMENT.
install_legacy_department_aliases()
