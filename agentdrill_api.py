
import json
from pathlib import Path

from core.engine import AgentDrillEngine, Scenario


class AgentDrill:
    """
    Generic testing interface for tool-using agents.

    Developers supply their own:
      - agent
      - environment
      - tools
      - verification rules
    """

    def __init__(self):
        self.engine = AgentDrillEngine()

    def test(
        self,
        agent,
        scenario,
        report_path=None,
    ):
        result = self.engine.run(scenario, agent)

        if report_path:
            self.save_report(result, report_path)

        return result

    def test_suite(
        self,
        agent_factory,
        scenarios,
        report_path=None,
    ):
        report = self.engine.run_suite(
            scenarios,
            agent_factory,
        )

        if report_path:
            self.save_report(report, report_path)

        return report

    @staticmethod
    def save_report(data, path):
        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                data,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )


def evaluate(agent, scenario, report_path=None):
    """Evaluate an agent against one custom scenario."""
    return AgentDrill().test(
        agent=agent,
        scenario=scenario,
        report_path=report_path,
    )


def evaluate_suite(
    agent_factory,
    scenarios,
    report_path=None,
):
    """Evaluate a fresh agent instance per scenario."""
    return AgentDrill().test_suite(
        agent_factory=agent_factory,
        scenarios=scenarios,
        report_path=report_path,
    )


__all__ = [
    "AgentDrill",
    "Scenario",
    "evaluate",
    "evaluate_suite",
]
