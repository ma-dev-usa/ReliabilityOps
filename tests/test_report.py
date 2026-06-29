from reliabilityops.classifier import classify
from reliabilityops.models import CheckResult
from reliabilityops.report import generate_markdown_report


def test_generates_markdown_report():
    result = CheckResult(
        service="orders-api",
        endpoint="/api/orders",
        status_code=500,
        latency_ms=1840,
        success=False,
        response_excerpt="database connection refused",
    )

    classification = classify(result)
    report = generate_markdown_report(result, classification)

    assert "# Incident Report" in report
    assert "orders-api" in report
    assert "Dependency/database failure" in report
