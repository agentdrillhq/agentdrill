import json
from pathlib import Path

from agents.refund_agents import DefensiveAgent
from agents.adversarial_agents import (
    OverRefundAgent,
    PartialRefundAgent,
    DuplicateRefundAgent,
    CustomerTamperingAgent,
)
from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


BENCHMARK_PATH = Path("agentdrill_benchmark.json")


def run_agent(agent_class, scenario):
    agent = agent_class()
    return run_scenario(scenario, agent)


def benchmark_safe_agent(scenarios):
    results = []

    for scenario in scenarios:
        result = run_agent(DefensiveAgent, scenario)
        results.append(result)

    passed = sum(result["passed"] for result in results)
    failed = len(results) - passed
    errors = sum(
        1
        for result in results
        if result.get("error")
    )

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "correctness": passed / len(results) if results else 0,
        "results": results,
    }


def benchmark_attacks(scenarios):
    attack_agents = [
        OverRefundAgent,
        PartialRefundAgent,
        DuplicateRefundAgent,
        CustomerTamperingAgent,
    ]

    # These are all scenarios where the correct outcome is a completed refund.
    # Attack agents should therefore be caught when they violate the contract.
    target_names = {
        "standard_refund_payment_5001",
        "alternate_customer_refund",
        "standard_refund_ticket_injection",
    }

    targets = [
        scenario
        for scenario in scenarios
        if scenario["name"] in target_names
    ]

    results = []

    for agent_class in attack_agents:
        for scenario in targets:
            result = run_agent(agent_class, scenario)

            results.append({
                "agent": agent_class.__name__,
                "scenario": scenario["name"],
                "passed": result["passed"],
                "error": result.get("error"),
                "verification": result.get("verification", {}),
            })

    detected = sum(
        1
        for result in results
        if not result["passed"] and not result["error"]
    )

    missed = sum(
        1
        for result in results
        if result["passed"]
    )

    errors = sum(
        1
        for result in results
        if result["error"]
    )

    total = len(results)

    return {
        "total": total,
        "detected": detected,
        "missed": missed,
        "errors": errors,
        "detection_rate": detected / total if total else 0,
        "target_scenarios": sorted(target_names),
        "results": results,
    }


def print_attack_details(attack_results):
    print()
    print("-" * 78)
    print("KNOWN ATTACK DETECTION")
    print("-" * 78)

    print(
        f"Target scenarios: "
        f"{len(attack_results['target_scenarios'])}"
    )
    print(
        f"Attack tests:     {attack_results['total']}"
    )
    print(
        f"Detected:         {attack_results['detected']}/"
        f"{attack_results['total']}"
    )
    print(
        f"Detection rate:   "
        f"{attack_results['detection_rate']:.2%}"
    )

    print()

    for result in attack_results["results"]:
        status = "DETECTED" if not result["passed"] else "MISSED"

        if result["error"]:
            status = "ERROR"

        print(
            f"{result['agent']:<28} "
            f"{result['scenario']:<38} "
            f"{status}"
        )

        verification = result["verification"]

        failed_rules = verification.get("failed_rules", [])

        if failed_rules:
            print(
                f"    Failed rules: {', '.join(failed_rules)}"
            )


def main():
    scenarios = generate_combined_scenarios()

    print("=" * 78)
    print("AGENTDRILL REFUND BENCHMARK")
    print("=" * 78)

    print(f"Scenarios: {len(scenarios)}")

    # ------------------------------------------------------------------
    # Safe-agent benchmark
    # ------------------------------------------------------------------

    safe_results = benchmark_safe_agent(scenarios)

    print()
    print("-" * 78)
    print("SAFE-AGENT CORRECTNESS")
    print("-" * 78)

    print(
        f"DefensiveAgent  "
        f"PASS {safe_results['passed']:>3}  "
        f"FAIL {safe_results['failed']:>3}  "
        f"ERROR {safe_results['errors']:>3}  "
        f"Correctness {safe_results['correctness']:.2%}"
    )

    # ------------------------------------------------------------------
    # Attack benchmark
    # ------------------------------------------------------------------

    attack_results = benchmark_attacks(scenarios)

    print_attack_details(attack_results)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    total_errors = (
        safe_results["errors"]
        + attack_results["errors"]
    )

    print()
    print("=" * 78)
    print("BENCHMARK SUMMARY")
    print("=" * 78)

    print(
        f"Safe-agent correctness: "
        f"{safe_results['correctness']:.2%}"
    )

    print(
        f"Known attack detection: "
        f"{attack_results['detection_rate']:.2%}"
    )

    print(
        f"Execution errors: {total_errors}"
    )

    report = {
        "scenarios": len(scenarios),
        "safe_agent": {
            "agent": "DefensiveAgent",
            "total": safe_results["total"],
            "passed": safe_results["passed"],
            "failed": safe_results["failed"],
            "errors": safe_results["errors"],
            "correctness": safe_results["correctness"],
        },
        "attack_detection": {
            "total": attack_results["total"],
            "detected": attack_results["detected"],
            "missed": attack_results["missed"],
            "errors": attack_results["errors"],
            "detection_rate": attack_results["detection_rate"],
            "target_scenarios": attack_results["target_scenarios"],
            "results": attack_results["results"],
        },
        "execution_errors": total_errors,
    }

    BENCHMARK_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print()
    print(f"JSON report saved to: {BENCHMARK_PATH.resolve()}")


if __name__ == "__main__":
    main()