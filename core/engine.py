
import copy
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class Scenario:
    name: str
    request: str = ""
    setup: Optional[Callable] = None
    make_tools: Optional[Callable] = None
    verify: Optional[Callable] = None
    metadata: Optional[dict] = None

    # Optional compatibility executor for existing domains.
    execute: Optional[Callable] = None


class AgentDrillEngine:
    """Shared entry point for business-agent evaluations."""

    def run(self, scenario, agent):
        started = time.perf_counter()

        # Compatibility path for a domain with an existing runner.
        if scenario.execute is not None:
            try:
                result = scenario.execute(agent)

                if not isinstance(result, dict):
                    raise TypeError(
                        "Scenario executor must return a dictionary"
                    )

                result = dict(result)
                result["scenario"] = scenario.name
                result["passed"] = (
                    result.get("passed") is True
                    and not result.get("agent_error")
                    and not result.get("verification_error")
                )

            except Exception as exc:
                result = {
                    "scenario": scenario.name,
                    "passed": False,
                    "agent_error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                    "verification_error": None,
                    "verification": {
                        "passed": False,
                        "failed_rules": ["execution_error"],
                    },
                    "agent_response": None,
                    "before": None,
                    "after": None,
                    "tool_events": [],
                }

            result["duration_seconds"] = round(
                time.perf_counter() - started, 4
            )

            return result

        # Native domain-independent scenario execution.
        if not all((
            scenario.setup,
            scenario.make_tools,
            scenario.verify,
        )):
            raise ValueError(
                "Scenario requires setup, make_tools and verify, "
                "or an execute adapter."
            )

        world = scenario.setup()
        before = copy.deepcopy(world.snapshot())
        tools = scenario.make_tools(world)

        agent_error = None
        agent_response = None

        try:
            agent_response = agent.run(
                tools=tools,
                request=scenario.request,
            )

        except Exception as exc:
            agent_error = f"{type(exc).__name__}: {exc}"

        after = copy.deepcopy(world.snapshot())
        verification_error = None

        try:
            verification = scenario.verify(
                before,
                after,
                world,
            )

            if not isinstance(verification, dict):
                raise TypeError(
                    "Verifier must return a dictionary"
                )

            if type(verification.get("passed")) is not bool:
                raise TypeError(
                    "Verifier must return a boolean passed field"
                )

        except Exception as exc:
            verification_error = (
                f"{type(exc).__name__}: {exc}"
            )

            verification = {
                "passed": False,
                "failed_rules": ["verifier_execution"],
                "message": verification_error,
            }

        passed = (
            agent_error is None
            and verification_error is None
            and verification["passed"] is True
        )

        return {
            "scenario": scenario.name,
            "passed": passed,
            "agent_error": agent_error,
            "verification_error": verification_error,
            "verification": verification,
            "agent_response": agent_response,
            "before": before,
            "after": after,
            "tool_events": copy.deepcopy(
                getattr(tools, "events", [])
            ),
            "duration_seconds": round(
                time.perf_counter() - started, 4
            ),
        }

    def run_suite(self, scenarios, agent_factory):
        results = []

        for scenario in scenarios:
            agent = agent_factory()
            result = self.run(scenario, agent)
            results.append(result)

        passed = sum(
            result["passed"] for result in results
        )

        total = len(results)

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": (
                    passed / total if total else 0
                ),
            },
            "results": results,
        }
