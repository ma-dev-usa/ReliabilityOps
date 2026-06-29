from dataclasses import dataclass, field
@dataclass
class CheckResult:
    service: str
    endpoint: str
    status_code: int
    latency_ms: int
    success: bool
    response_excerpt: str = ""
    missing_fields: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "CheckResult":
        return cls(
            service=data.get("service", "unknown-service"),
            endpoint=data.get("endpoint", "unknown-endpoint"),
            status_code=int(data.get("status_code", 0)),
            latency_ms=int(data.get("latency_ms", 0)),
            success=bool(data.get("success", False)),
            response_excerpt=data.get("response_excerpt", ""),
            missing_fields=data.get("missing_fields", []),
        )


@dataclass
class IncidentClassification:
    category: str
    severity: str
    confidence: int
    evidence: list[str]
    recommended_actions: list[str]
