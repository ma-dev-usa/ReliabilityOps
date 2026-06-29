from reliabilityops.classifier import classify
from reliabilityops.models import CheckResult


def test_classifies_auth_failure():
    result = CheckResult(
        service="auth-api",
        endpoint="/api/login",
        status_code=401,
        latency_ms=200,
        success=False,
        response_excerpt="invalid token",
    )

    classification = classify(result)

    assert classification.category == "Authentication failure"
    assert classification.confidence >= 80


def test_classifies_timeout_failure():
    result = CheckResult(
        service="inventory-api",
        endpoint="/api/inventory",
        status_code=504,
        latency_ms=5200,
        success=False,
        response_excerpt="gateway timeout",
    )

    classification = classify(result)

    assert classification.category == "Timeout / latency breach"
    assert classification.severity == "High"


def test_classifies_dependency_failure():
    result = CheckResult(
        service="orders-api",
        endpoint="/api/orders",
        status_code=500,
        latency_ms=1200,
        success=False,
        response_excerpt="database connection refused",
    )

    classification = classify(result)

    assert classification.category == "Dependency/database failure"
