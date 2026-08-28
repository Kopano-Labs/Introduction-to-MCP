"""Governed analytical operators for KPCB+ / GSMB context records.

This module gives KPCB+ a lightweight analytical projection layer inspired by
formal data-science operations such as groupby, pivot tables and heatmaps.
It deliberately does not depend on Pandas/Dask: KMEC owns scalable statistical
execution. KPCB+ owns protocol/context semantics and provenance preservation.

Core invariants:
- UNKNOWN is not VIOLATED.
- filesystem depth is not authority.
- aggregates are projections, not source truth.
- heat/attention is not action permission.
- every aggregate remains traceable to source record IDs/paths.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import product
from typing import Any, Iterable, Mapping, Sequence

from .kpcb_plus import KPCBBlock


UNKNOWN = "UNKNOWN"


class KPCBAnalyticsError(ValueError):
    """Raised when an analytical projection request is structurally invalid."""


class KPCBAnalyticalCorpus:
    """Immutable-in-practice corpus of governed KPCB+/Markdown observations.

    Records are copied on admission and on output so analytical projections do
    not mutate source testimony. A record MUST have a stable ``record_id`` and
    ``path``. Missing epistemic fields are preserved as ``UNKNOWN`` rather than
    being silently interpreted as failure.
    """

    def __init__(self, records: Iterable[Mapping[str, Any]]):
        normalized = [self._normalize_record(record) for record in records]
        ids = [record["record_id"] for record in normalized]
        if len(ids) != len(set(ids)):
            raise KPCBAnalyticsError("record_id values must be unique")
        self._records = tuple(normalized)

    @classmethod
    def from_kpcb_blocks(
        cls,
        blocks: Iterable[Mapping[str, Any]],
    ) -> "KPCBAnalyticalCorpus":
        """Build governed observations from raw KPCB+ blocks.

        Each item must provide ``record_id``, ``path`` and ``raw``. Additional
        metadata is retained. KPCB+ parsing supplies hierarchy/title,
        ``protocol_channels`` and compiler validation state. Testimony state is
        NEVER inferred from channel presence and defaults to UNKNOWN unless the
        caller explicitly supplies it.
        """
        records: list[dict[str, Any]] = []
        for item in blocks:
            if "raw" not in item:
                raise KPCBAnalyticsError("KPCB block input requires raw")
            block = KPCBBlock(str(item["raw"]))
            validation = block.validate()
            record = dict(item)
            record.pop("raw", None)
            record.setdefault("title", block.hierarchy or "UNNAMED")
            record.setdefault("keynote", block.keynote)
            record.setdefault("protocol_channels", list(validation["channels"]))
            record.setdefault("validation_state", validation["verdict"])
            record.setdefault("testimony_state", UNKNOWN)
            records.append(record)
        return cls(records)

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(record) for record in self._records)

    def group_by(self, *dimensions: str) -> dict[str, Any]:
        """Group governed records by one or more semantic dimensions.

        Sequence-valued dimensions (for example ``protocol_channels``) are
        exploded so one record may truthfully participate in multiple groups.
        Group order and member order are deterministic regardless of input
        record order.
        """
        dims = self._require_dimensions(dimensions)
        grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}

        for record in self._records:
            value_sets = [self._dimension_values(record, dim) for dim in dims]
            for key in product(*value_sets):
                grouped.setdefault(tuple(key), []).append(record)

        groups = []
        for key in sorted(grouped, key=self._sort_key):
            members = sorted(grouped[key], key=lambda item: str(item["record_id"]))
            groups.append(
                {
                    "key": {dim: value for dim, value in zip(dims, key)},
                    "count": len(members),
                    "record_ids": [member["record_id"] for member in members],
                    "paths": [member["path"] for member in members],
                }
            )

        return {
            "operation": "GROUP",
            "dimensions": list(dims),
            "groups": groups,
            "claims": self._non_authoritative_claims(),
        }

    def pivot(
        self,
        row_dimension: str,
        column_dimension: str,
        *,
        value: str | None = None,
        aggregation: str = "count",
    ) -> dict[str, Any]:
        """Re-project the same corpus across row/column dimensions.

        Supported aggregations:
        - ``count``: number of source records contributing to the cell.
        - ``sum``: numeric sum of ``value`` across contributing source records.

        Every cell preserves source record IDs and paths.
        """
        self._require_dimensions((row_dimension, column_dimension))
        if aggregation not in {"count", "sum"}:
            raise KPCBAnalyticsError("aggregation must be 'count' or 'sum'")
        if aggregation == "sum" and not value:
            raise KPCBAnalyticsError("sum aggregation requires value")

        cells: dict[tuple[Any, Any], dict[str, Any]] = {}
        row_values: set[Any] = set()
        column_values: set[Any] = set()

        for record in self._records:
            rows = self._dimension_values(record, row_dimension)
            columns = self._dimension_values(record, column_dimension)
            for row_value, column_value in product(rows, columns):
                row_values.add(row_value)
                column_values.add(column_value)
                key = (row_value, column_value)
                cell = cells.setdefault(
                    key,
                    {"value": 0, "record_ids": [], "paths": []},
                )
                if aggregation == "count":
                    increment = 1
                else:
                    raw_value = record.get(value, 0)
                    if raw_value in (None, UNKNOWN):
                        increment = 0
                    elif isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
                        increment = raw_value
                    else:
                        raise KPCBAnalyticsError(
                            f"sum value {value!r} must be numeric or missing; "
                            f"record {record['record_id']!r} supplied {raw_value!r}"
                        )
                cell["value"] += increment
                cell["record_ids"].append(record["record_id"])
                cell["paths"].append(record["path"])

        ordered_rows = sorted(row_values, key=self._sort_atom)
        ordered_columns = sorted(column_values, key=self._sort_atom)
        matrix = []
        provenance = []
        for row_value in ordered_rows:
            matrix_row = []
            provenance_row = []
            for column_value in ordered_columns:
                cell = cells.get((row_value, column_value))
                if cell is None:
                    matrix_row.append(0)
                    provenance_row.append({"record_ids": [], "paths": []})
                else:
                    matrix_row.append(cell["value"])
                    provenance_row.append(
                        {
                            "record_ids": sorted(cell["record_ids"], key=str),
                            "paths": sorted(cell["paths"], key=str),
                        }
                    )
            matrix.append(matrix_row)
            provenance.append(provenance_row)

        return {
            "operation": "PIVOT",
            "row_dimension": row_dimension,
            "column_dimension": column_dimension,
            "aggregation": aggregation,
            "value_field": value,
            "row_labels": ordered_rows,
            "column_labels": ordered_columns,
            "matrix": matrix,
            "provenance": provenance,
            "claims": self._non_authoritative_claims(),
        }

    def attention_matrix(
        self,
        row_dimension: str,
        column_dimension: str,
        *,
        value: str | None = None,
        aggregation: str = "count",
        reason: str = "attention_density",
    ) -> dict[str, Any]:
        """Emit heatmap-ready data without granting authority or action.

        This is deliberately a data matrix, not a renderer. UI layers may map
        numeric intensity to color, but the matrix itself carries explicit
        governance claims preventing visual intensity from becoming truth.
        """
        projection = self.pivot(
            row_dimension,
            column_dimension,
            value=value,
            aggregation=aggregation,
        )
        return {
            **projection,
            "operation": "ATTENTION_MATRIX",
            "reason": reason,
            "render_hint": "heatmap",
            "claims": {
                **self._non_authoritative_claims(),
                "attention_only": True,
                "action_permission": False,
            },
        }

    def trace_cell(
        self,
        projection: Mapping[str, Any],
        row_label: Any,
        column_label: Any,
    ) -> dict[str, Any]:
        """Recover source records that contributed to one pivot/heatmap cell."""
        rows = list(projection.get("row_labels", []))
        columns = list(projection.get("column_labels", []))
        try:
            row_index = rows.index(row_label)
            column_index = columns.index(column_label)
        except ValueError as exc:
            raise KPCBAnalyticsError("row/column label is not present in projection") from exc

        provenance = projection.get("provenance")
        if not isinstance(provenance, Sequence):
            raise KPCBAnalyticsError("projection has no provenance matrix")
        cell = provenance[row_index][column_index]
        ids = set(cell.get("record_ids", []))
        records = [deepcopy(record) for record in self._records if record["record_id"] in ids]
        records.sort(key=lambda record: str(record["record_id"]))
        return {
            "row_label": row_label,
            "column_label": column_label,
            "record_ids": [record["record_id"] for record in records],
            "paths": [record["path"] for record in records],
            "records": records,
        }

    @staticmethod
    def _normalize_record(record: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(record, Mapping):
            raise KPCBAnalyticsError("records must be mappings")
        if not record.get("record_id"):
            raise KPCBAnalyticsError("record_id is required")
        if not record.get("path"):
            raise KPCBAnalyticsError("path is required")

        normalized = deepcopy(dict(record))
        normalized.setdefault("title", UNKNOWN)
        normalized.setdefault("depth", UNKNOWN)
        normalized.setdefault("canonical_index", UNKNOWN)
        normalized.setdefault("project", UNKNOWN)
        normalized.setdefault("protocol_channels", [])
        normalized.setdefault("artifact_type", UNKNOWN)
        normalized.setdefault("authority", UNKNOWN)
        normalized.setdefault("validation_state", UNKNOWN)
        normalized.setdefault("testimony_state", UNKNOWN)
        normalized.setdefault("sprint", UNKNOWN)
        normalized.setdefault("ecosystem", UNKNOWN)
        normalized.setdefault("evidence_count", 0)
        return normalized

    def _require_dimensions(self, dimensions: Sequence[str]) -> tuple[str, ...]:
        dims = tuple(dimensions)
        if not dims:
            raise KPCBAnalyticsError("at least one dimension is required")
        for dim in dims:
            if not isinstance(dim, str) or not dim.strip():
                raise KPCBAnalyticsError("dimensions must be non-empty strings")
        return dims

    @staticmethod
    def _dimension_values(record: Mapping[str, Any], dimension: str) -> tuple[Any, ...]:
        value = record.get(dimension, UNKNOWN)
        if value is None:
            return (UNKNOWN,)
        if isinstance(value, (list, tuple, set, frozenset)):
            values = tuple(value)
            return values if values else (UNKNOWN,)
        return (value,)

    @classmethod
    def _sort_key(cls, key: tuple[Any, ...]) -> tuple[str, ...]:
        return tuple(cls._sort_atom(value) for value in key)

    @staticmethod
    def _sort_atom(value: Any) -> str:
        return f"{type(value).__name__}:{value!s}"

    @staticmethod
    def _non_authoritative_claims() -> dict[str, bool]:
        return {
            "source_truth_replaced": False,
            "causal": False,
            "authority_inferred": False,
            "action_permission": False,
        }
