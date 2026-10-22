
from core.engine import Scenario

from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


def normalize_verification(verification):
    verification = verification or {}

    results = verification.get("results", [])

    failed_rules = [
        item.get("rule", "unknown")
        for item in results
        if not item.get("passed", False)
    ]

    return {
        "passed": verification.get("passed") is True,
        "failed_rules": failed_rules,
        "results": results,
    }


def make_refund_scenario(legacy_scenario):
    """Adapt a refund scenario to AgentDrill's shared interface."""

    def execute(agent):
        result = run_scenario(legacy_scenario, agent)

        verification = normalize_verification(
            result.get("verification")
        )

        error = result.get("error")

        return {
            "passed": (
                result.get("passed") is True
                and not error
            ),
            "agent_error": error,
            "verification_error": None,
            "verification": verification,
            "agent_response": None,
            "before": None,
            "after": result.get("final_state"),
            "tool_events": result.get("trace") or [],
            "expected_outcome": result.get("expected_outcome"),
        }

    return Scenario(
        name=legacy_scenario["name"],
        request=legacy_scenario.get("request", ""),
        metadata={
            "domain": "refunds",
            "adapter": "legacy_runner",
        },
        execute=execute,
    )


def get_refund_scenarios():
    return [
        make_refund_scenario(scenario)
        for scenario in generate_combined_scenarios()
    ]
