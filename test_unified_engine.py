
import json
from pathlib import Path

from core.engine import AgentDrillEngine
from core.refund_adapter import get_refund_scenarios

from examples.crm_demo import (
    make_scenario,
    SafeCRMAgent,
    UnsafeCRMAgent,
)

from examples.my_agent import Agent as RefundAgent


REPORT_PATH = Path("agentdrill_unified_report.json")


def main():
    engine = AgentDrillEngine()

    print("=" * 65)
    print("AGENTDRILL v0.3.1 - UNIFIED ENGINE VALIDATION")
    print("=" * 65)

    # CRM uses the native generic engine.
    crm_scenario = make_scenario()

    crm_safe = engine.run(
        crm_scenario,
        SafeCRMAgent(),
    )

    crm_unsafe = engine.run(
        crm_scenario,
        UnsafeCRMAgent(),
    )

    print()
    print("DOMAIN: CRM")
    print(
        "Safe agent:",
        "PASS" if crm_safe["passed"] else "FAIL",
    )
    print(
        "Unsafe agent detected:",
        not crm_unsafe["passed"],
    )

    # Refunds use the compatibility adapter.
    refund_scenarios = get_refund_scenarios()

    refund_report = engine.run_suite(
        refund_scenarios,
        agent_factory=RefundAgent,
    )

    summary = refund_report["summary"]

    print()
    print("DOMAIN: REFUNDS")
    print("Scenarios:", summary["total"])
    print("Passed:", summary["passed"])
    print("Failed:", summary["failed"])
    print(f"Pass rate: {summary['pass_rate']:.2%}")

    for result in refund_report["results"]:
        status = (
            "PASS" if result["passed"] else "FAIL"
        )

        print(
            f"{result['scenario']:<45} {status}"
        )

        if not result["passed"]:
            print(
                "  Failed rules:",
                result["verification"].get(
                    "failed_rules", []
                ),
            )

            if result.get("agent_error"):
                print(
                    "  Agent error:",
                    result["agent_error"],
                )

    report = {
        "version": "0.3.1",
        "crm": {
            "safe_agent": crm_safe,
            "unsafe_agent": crm_unsafe,
        },
        "refunds": refund_report,
    }

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    # Assertions make validation fail if anything regresses.
    assert crm_safe["passed"] is True
    assert crm_unsafe["passed"] is False

    assert (
        "account_credit_unchanged"
        in crm_unsafe["verification"]["failed_rules"]
    )

    assert summary["total"] == 18
    assert summary["passed"] == 18
    assert summary["failed"] == 0

    print()
    print("=" * 65)
    print("UNIFIED ENGINE VALIDATION: PASS")
    print("=" * 65)
    print("Domains tested: refunds, CRM")
    print("Report:", REPORT_PATH.resolve())


if __name__ == "__main__":
    main()
