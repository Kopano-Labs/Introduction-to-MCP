from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PortingTask:
    key: str
    description: str

__all__ = ['PortingTask']
