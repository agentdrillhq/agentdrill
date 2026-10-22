
import json
import time
from datetime import datetime
from pathlib import Path

from agents.ollama_agent import OllamaRefundAgent
from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


REPORT_PATH = Path("agentdrill_ollama_benchmark.json")


def get_failed_rules(result):
    verification = result.get("verification") or {}

    return [
        item.get("rule", "unknown")
        for item in verification.get("results", [])
        if not item.get("passed", False)
    ]


def get_refunds(result):
    state = result.get("final_state") or {}
    return state.get("refunds", [])


def save_report(report):
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )


def main():
    scenarios = generate_combined_scenarios()

    agent = OllamaRefundAgent(
        model="qwen3:4b",
        max_rounds=12,
    )

    report = {
        "benchmark": "AgentDrill Real AI Agent Benchmark",
        "model": agent.model,
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(scenarios),
        "results": [],
        "summary": {},
    }

    print("=" * 75)
    print("AGENTDRILL - REAL AI AGENT BENCHMARK")
    print("=" * 75)
    print("Model:", agent.model)
    print("Total scenarios:", len(scenarios))
    print("Report:", REPORT_PATH.resolve())
    print("=" * 75)

    for index, scenario in enumerate(scenarios, start=1):
        name = scenario["name"]

        print()
        print("=" * 75)
        print(f"TEST {index}/{len(scenarios)}: {name}")
        print("=" * 75)

        start = time.perf_counter()

        try:
            result = run_scenario(scenario, agent)
            duration = round(time.perf_counter() - start, 2)

            error = result.get("error")
            passed = bool(result.get("passed"))

            if error:
                status = "ERROR"
            elif passed:
                status = "PASS"
            else:
                status = "FAIL"

            failed_rules = get_failed_rules(result)
            refunds = get_refunds(result)

            record = {
                "scenario": name,
                "status": status,
                "passed": passed,
                "expected_outcome": result.get("expected_outcome"),
                "execution_error": error,
                "failed_rules": failed_rules,
                "duration_seconds": duration,
                "tool_trace": result.get("trace", []),
                "final_refunds": refunds,
                "verification": result.get("verification"),
            }

        except Exception as exc:
            duration = round(time.perf_counter() - start, 2)

            status = "ERROR"

            record = {
                "scenario": name,
                "status": status,
                "passed": False,
                "expected_outcome": None,
                "execution_error": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "failed_rules": [],
                "duration_seconds": duration,
                "tool_trace": [],
                "final_refunds": [],
                "verification": None,
            }

        report["results"].append(record)

        print()
        print("-" * 75)
        print("RESULT:", status)
        print("Expected outcome:", record["expected_outcome"])
        print("Execution time:", duration, "seconds")
        print("Refund records:", len(record["final_refunds"]))

        if record["failed_rules"]:
            print(
                "Failed rules:",
                ", ".join(record["failed_rules"]),
            )

        if record["execution_error"]:
            print(
                "Execution error:",
                record["execution_error"],
            )

        # Save immediately, so completed results survive
        # even if a later model call hangs or is interrupted.
        save_report(report)

    passed = sum(
        r["status"] == "PASS"
        for r in report["results"]
    )

    failed = sum(
        r["status"] == "FAIL"
        for r in report["results"]
    )

    errors = sum(
        r["status"] == "ERROR"
        for r in report["results"]
    )

    total = len(report["results"])

    report["summary"] = {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
        "pass_rate": passed / total if total else 0,
    }

    save_report(report)

    print()
    print("=" * 75)
    print("AGENTDRILL - FINAL REAL AI BENCHMARK RESULTS")
    print("=" * 75)

    for record in report["results"]:
        print(
            f"{record['scenario']:<45} "
            f"{record['status']}"
        )

    print()
    print("-" * 75)
    print(f"TOTAL:      {total}")
    print(f"PASSED:     {passed}")
    print(f"FAILED:     {failed}")
    print(f"ERRORS:     {errors}")
    print(f"PASS RATE:  {passed / total:.2%}" if total else "PASS RATE: N/A")
    print("-" * 75)
    print()
    print("Full JSON report:", REPORT_PATH.resolve())


if __name__ == "__main__":
    main()
