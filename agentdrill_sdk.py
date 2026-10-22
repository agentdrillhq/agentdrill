
import importlib.util
from pathlib import Path

from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


class AgentDrillError(Exception):
    pass


def load_agent(agent_path):
    path = Path(agent_path).resolve()

    if not path.is_file():
        raise AgentDrillError(
            f"Agent file not found: {path}"
        )

    spec = importlib.util.spec_from_file_location(
        "agentdrill_external_agent",
        path,
    )

    if spec is None or spec.loader is None:
        raise AgentDrillError(
            "Could not load agent module"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    agent_class = getattr(module, "Agent", None)

    if agent_class is None:
        raise AgentDrillError(
            "Agent file must define a class named Agent"
        )

    agent = agent_class()

    if not callable(getattr(agent, "run", None)):
        raise AgentDrillError(
            "Agent must implement run(tools, request, "
            "ticket=None, contract=None)"
        )

    return agent


def get_scenarios():
    return generate_combined_scenarios()


def evaluate(agent_path, scenario_name=None):
    scenarios = get_scenarios()

    if scenario_name:
        scenarios = [
            scenario
            for scenario in scenarios
            if scenario["name"] == scenario_name
        ]

        if not scenarios:
            raise AgentDrillError(
                f"Unknown scenario: {scenario_name}"
            )

    results = []

    for scenario in scenarios:
        # Fresh agent instance for each scenario.
        agent = load_agent(agent_path)

        result = run_scenario(scenario, agent)
        verification = result.get("verification") or {}

        failed_rules = [
            item.get("rule", "unknown")
            for item in verification.get("results", [])
            if not item.get("passed", False)
        ]

        results.append({
            "scenario": scenario["name"],
            "passed": bool(result.get("passed")),
            "expected_outcome": result.get("expected_outcome"),
            "error": result.get("error"),
            "failed_rules": failed_rules,
            "tool_trace": result.get("trace", []),
            "final_state": result.get("final_state"),
            "verification": verification,
        })

    passed = sum(
        result["passed"]
        for result in results
    )

    return {
        "agent_path": str(Path(agent_path).resolve()),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "pass_rate": (
                passed / len(results)
                if results else 0
            ),
        },
        "results": results,
    }
