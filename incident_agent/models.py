from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Alert:
    alert_id: str
    service: str
    component: str
    error_type: str
    error_code: str
    message: str
    infrastructure: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryMatch:
    bank_id: str
    text: str
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IncidentResponse:
    fingerprint: str
    affected_alerts: int
    diagnosis: str
    recommended_action: str
    memory_matches: tuple[MemoryMatch, ...] = ()
