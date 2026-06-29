import time
from urllib.parse import urlparse

import requests
import yaml

from reliabilityops.models import CheckResult


def load_checks(config_path: str) -> list[dict]:
    with open(config_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data.get("services", [])


def run_check(service: dict) -> CheckResult:
    name = service["name"]
    url = service["url"]
    method = service.get("method", "GET").upper()
    expected_status = int(service.get("expected_status", 200))
    timeout_ms = int(service.get("timeout_ms", 1000))
    required_fields = service.get("required_fields", [])

    endpoint = urlparse(url).path or url

    start = time.perf_counter()

    try:
        response = requests.request(method, url, timeout=timeout_ms / 1000)
        latency_ms = int((time.perf_counter() - start) * 1000)

        missing_fields = []
        response_json = None

        try:
            response_json = response.json()
        except ValueError:
            response_json = None

        if isinstance(response_json, dict):
            missing_fields = [field for field in required_fields if field not in response_json]

        success = (
            response.status_code == expected_status
            and latency_ms <= timeout_ms
            and not missing_fields
        )

        return CheckResult(
            service=name,
            endpoint=endpoint,
            status_code=response.status_code,
            latency_ms=latency_ms,
            success=success,
            response_excerpt=response.text[:500],
            missing_fields=missing_fields,
        )

    except requests.RequestException as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            service=name,
            endpoint=endpoint,
            status_code=0,
            latency_ms=latency_ms,
            success=False,
            response_excerpt=str(exc),
            missing_fields=[],
        )


def run_config(config_path: str) -> list[CheckResult]:
    checks = load_checks(config_path)
    return [run_check(service) for service in checks]
