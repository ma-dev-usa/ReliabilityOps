from reliabilityops.classifier import classify
from reliabilityops.models import CheckResult
from reliabilityops.storage import save_incident, get_history


def test_saves_incident_history(tmp_path):
    db_path = tmp_path / "test.db"

    result = CheckResult(
        service="orders-api",
        endpoint="/api/orders",
        status_code=500,
        latency_ms=1840,
        success=False,
        response_excerpt="database connection refused",
    )

    classification = classify(result)
    save_incident(result, classification, str(db_path))

    history = get_history(str(db_path))

    assert len(history) == 1
    assert history[0][0] == "orders-api"
