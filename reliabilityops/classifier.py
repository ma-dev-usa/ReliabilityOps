from reliabilityops.models import CheckResult, IncidentClassification
def classify(result: CheckResult) -> IncidentClassification:
    text = result.response_excerpt.lower()
    evidence = []

    if result.success:
        return IncidentClassification(
            category="Healthy",
            severity="Low",
            confidence=99,
            evidence=["Endpoint matched expected status, latency, and response validation rules."],
            recommended_actions=["No action required."],
        )

    if result.status_code:
        evidence.append(f"HTTP status code: {result.status_code}")

    if result.latency_ms:
        evidence.append(f"Observed latency: {result.latency_ms}ms")

    if result.missing_fields:
        evidence.append(f"Missing required response fields: {', '.join(result.missing_fields)}")

    if result.response_excerpt:
        evidence.append(f"Response excerpt: {result.response_excerpt[:180]}")

    if result.status_code in (401, 403) or any(term in text for term in [
        "unauthorized", "forbidden", "invalid token", "missing authorization", "missing token"
    ]):
        return IncidentClassification(
            category="Authentication failure",
            severity="High",
            confidence=91,
            evidence=evidence,
            recommended_actions=[
                "Verify API credentials and authorization headers.",
                "Check token expiration and identity provider configuration.",
                "Confirm the service account has permission for this endpoint.",
            ],
        )

    if result.latency_ms >= 3000 or result.status_code in (408, 504) or "timeout" in text:
        return IncidentClassification(
            category="Timeout / latency breach",
            severity="High",
            confidence=88,
            evidence=evidence,
            recommended_actions=[
                "Check upstream service latency and recent deployment changes.",
                "Review database query duration and connection pool saturation.",
                "Increase timeout only after confirming the endpoint behavior is expected.",
            ],
        )

    if result.missing_fields or any(term in text for term in [
        "schema", "missing field", "invalid response", "unexpected field"
    ]):
        return IncidentClassification(
            category="Schema mismatch",
            severity="Medium",
            confidence=86,
            evidence=evidence,
            recommended_actions=[
                "Compare the response payload against the expected API contract.",
                "Check whether a backend or frontend contract changed recently.",
                "Update tests or rollback the incompatible API change.",
            ],
        )

    if any(term in text for term in [
        "missing env", "environment variable", "api key", "missing config", "invalid config", "configuration"
    ]):
        return IncidentClassification(
            category="Missing environment/config value",
            severity="High",
            confidence=84,
            evidence=evidence,
            recommended_actions=[
                "Verify required environment variables are present.",
                "Check deployment secrets and runtime configuration.",
                "Confirm configuration values were loaded in the target environment.",
            ],
        )

    if any(term in text for term in [
        "connection refused", "database", "postgres", "mysql", "redis",
        "dependency", "upstream", "unavailable", "could not connect"
    ]):
        return IncidentClassification(
            category="Dependency/database failure",
            severity="High",
            confidence=92,
            evidence=evidence,
            recommended_actions=[
                "Verify database or upstream dependency availability.",
                "Check connection strings, credentials, and network access.",
                "Review recent infrastructure or deployment changes.",
            ],
        )

    if 500 <= result.status_code <= 599:
        return IncidentClassification(
            category="HTTP 5xx server error",
            severity="High",
            confidence=82,
            evidence=evidence,
            recommended_actions=[
                "Review application logs for stack traces or unhandled exceptions.",
                "Check recent deployments and rollback if the failure started after release.",
                "Verify dependent services are healthy.",
            ],
        )

    return IncidentClassification(
        category="Unknown failure",
        severity="Medium",
        confidence=55,
        evidence=evidence or ["No high-confidence failure signature found."],
        recommended_actions=[
            "Review raw response body and service logs.",
            "Check recent deployments, configuration changes, and dependency health.",
            "Add a new classifier rule if this failure pattern repeats.",
        ],
    )
