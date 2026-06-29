import argparse
import json

from reliabilityops.checker import run_config
from reliabilityops.classifier import classify
from reliabilityops.models import CheckResult
from reliabilityops.report import write_report
from reliabilityops.storage import save_incident, get_history


def print_classification(result: CheckResult) -> None:
    classification = classify(result)

    print("\nReliabilityOps Incident Triage")
    print("=" * 34)
    print(f"Service: {result.service}")
    print(f"Endpoint: {result.endpoint}")
    print(f"Status Code: {result.status_code}")
    print(f"Latency: {result.latency_ms}ms")
    print(f"Success: {result.success}")
    print(f"Classification: {classification.category}")
    print(f"Severity: {classification.severity}")
    print(f"Confidence: {classification.confidence}%")

    print("\nEvidence:")
    for item in classification.evidence:
        print(f"- {item}")

    print("\nRecommended Actions:")
    for idx, item in enumerate(classification.recommended_actions, start=1):
        print(f"{idx}. {item}")


def handle_report(args: argparse.Namespace) -> None:
    with open(args.incident, "r", encoding="utf-8") as file:
        data = json.load(file)

    result = CheckResult.from_dict(data)
    classification = classify(result)
    output_path = write_report(result, classification)

    print_classification(result)
    print(f"\nReport written to: {output_path}")


def handle_run(args: argparse.Namespace) -> None:
    results = run_config(args.config)

    for result in results:
        classification = classify(result)
        print_classification(result)
        save_incident(result, classification, args.db)

        if not result.success:
            output_path = write_report(result, classification)
            print(f"\nReport written to: {output_path}")


def handle_history(args: argparse.Namespace) -> None:
    rows = get_history(args.db)

    if not rows:
        print("No incident history found.")
        return

    print("\nRecent Incident History")
    print("=" * 24)

    for row in rows:
        service, endpoint, category, severity, confidence, status_code, latency_ms, created_at = row
        print(
            f"{created_at} | {service} | {endpoint} | {category} | "
            f"{severity} | {confidence}% | HTTP {status_code} | {latency_ms}ms"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="reliabilityops",
        description="API incident triage and runbook automation CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run API checks from a YAML config")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--db", default="reliabilityops.db")
    run_parser.set_defaults(func=handle_run)

    report_parser = subparsers.add_parser("report", help="Generate report from an incident JSON file")
    report_parser.add_argument("--incident", required=True)
    report_parser.set_defaults(func=handle_report)

    history_parser = subparsers.add_parser("history", help="Show recent incident history")
    history_parser.add_argument("--db", default="reliabilityops.db")
    history_parser.set_defaults(func=handle_history)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
