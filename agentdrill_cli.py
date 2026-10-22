
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from agentdrill import evaluate
from agentdrill_sdk import (
    AgentDrillError,
    evaluate as evaluate_refunds,
    get_scenarios,
)


def load_custom_module(file_path):
    path = Path(file_path).resolve()

    if not path.is_file():
        raise AgentDrillError(
            f"Custom test file not found: {path}"
        )

    spec = importlib.util.spec_from_file_location(
        "agentdrill_custom_test",
        path,
    )

    if spec is None or spec.loader is None:
        raise AgentDrillError(
            "Unable to load custom test module"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise

    return module


def run_custom(args):
    module = load_custom_module(args.file)

    scenario = getattr(module, "scenario", None)
    agent_class = getattr(module, "Agent", None)

    if scenario is None:
        raise AgentDrillError(
            "Custom test file must define 'scenario'"
        )

    if not isinstance(agent_class, type):
        raise AgentDrillError(
            "Custom test file must define an 'Agent' class"
        )

    agent = agent_class()

    if not callable(getattr(agent, "run", None)):
        raise AgentDrillError(
            "Agent must implement run(tools, request)"
        )

    print("=" * 65)
    print("AGENTDRILL - CUSTOM AGENT EVALUATION")
    print("=" * 65)
    print("Scenario:", scenario.name)
    print("Agent:", agent_class.__name__)

    result = evaluate(
        agent,
        scenario,
        report_path=args.output,
    )

    status = "PASS" if result["passed"] else "FAIL"

    print()
    print("Result:", status)

    verification = result.get("verification") or {}

    print(
        "Failed rules:",
        verification.get("failed_rules", []),
    )

    print(
        "Tool events:",
        len(result.get("tool_events") or []),
    )

    if result.get("agent_error"):
        print(
            "Agent error:",
            result["agent_error"],
        )

    if result.get("verification_error"):
        print(
            "Verification error:",
            result["verification_error"],
        )

    print()
    print("Report:", Path(args.output).resolve())

    return 0 if result["passed"] else 1


def run_refunds(args):
    report = evaluate_refunds(
        agent_path=args.agent,
        scenario_name=args.scenario,
    )

    print()
    print("=" * 65)
    print("AGENTDRILL - REFUND AGENT EVALUATION")
    print("=" * 65)

    for result in report["results"]:
        if result.get("error"):
            status = "ERROR"
        elif result["passed"]:
            status = "PASS"
        else:
            status = "FAIL"

        print(
            f"{result['scenario']:<45} {status}"
        )

        if result.get("failed_rules"):
            print(
                "  Failed rules:",
                ", ".join(result["failed_rules"]),
            )

        if result.get("error"):
            print(
                "  Error:",
                result["error"],
            )

    summary = report["summary"]

    print()
    print("-" * 65)
    print("Total:", summary["total"])
    print("Passed:", summary["passed"])
    print("Failed:", summary["failed"])
    print(f"Pass rate: {summary['pass_rate']:.2%}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )

    print()
    print("Report:", output.resolve())

    return 0 if summary["failed"] == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        prog="agentdrill",
        description=(
            "Test AI agents against business-state rules."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "list",
        help="List bundled refund scenarios",
    )

    test_parser = subparsers.add_parser(
        "test",
        help="Test an agent against bundled refund scenarios",
    )

    test_parser.add_argument(
        "--agent",
        required=True,
    )

    test_parser.add_argument(
        "--scenario",
        default=None,
    )

    test_parser.add_argument(
        "--output",
        default="agentdrill_external_report.json",
    )

    custom_parser = subparsers.add_parser(
        "custom",
        help="Run a developer-defined agent and scenario",
    )

    custom_parser.add_argument(
        "--file",
        required=True,
        help=(
            "Python file defining 'scenario' and 'Agent'"
        ),
    )

    custom_parser.add_argument(
        "--output",
        default="agentdrill_custom_report.json",
    )

    args = parser.parse_args()

    try:
        if args.command == "list":
            for scenario in get_scenarios():
                print(scenario["name"])
            return 0

        if args.command == "test":
            return run_refunds(args)

        if args.command == "custom":
            return run_custom(args)

    except Exception as exc:
        print(
            f"AgentDrill error: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    return 2


if __name__ == "__main__":
    sys.exit(main())
