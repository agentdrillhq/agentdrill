
import json

from agents.ollama_agent import OllamaRefundAgent
from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


class SimulatedToolCallingAgent(OllamaRefundAgent):
    def __init__(self):
        super().__init__()
        self.responses = iter([
            {
                "message": {
                    "content": "",
                    "tool_calls": [{
                        "function": {
                            "name": "lookup_customer",
                            "arguments": {"customer_id": "C001"},
                        }
                    }],
                }
            },
            {
                "message": {
                    "content": "",
                    "tool_calls": [{
                        "function": {
                            "name": "issue_refund",
                            "arguments": {
                                "payment_id": "P100",
                                "amount": 50000,
                            },
                        }
                    }],
                }
            },
            {
                "message": {
                    "content": "Finished",
                    "tool_calls": [],
                }
            },
        ])

    def chat(self, messages, definitions):
        return next(self.responses)


def main():
    scenarios = generate_combined_scenarios()

    scenario = next(
        s for s in scenarios
        if s["name"] == "standard_refund_payment_5001"
    )

    agent = SimulatedToolCallingAgent()

    result = run_scenario(scenario, agent)

    events = agent.tool_events

    assert len(events) == 2, events
    assert events[0]["tool"] == "lookup_customer"
    assert events[0]["status"] == "SUCCESS"
    assert events[1]["tool"] == "issue_refund"
    assert events[1]["authorized_arguments"] is False

    print()
    print("=" * 65)
    print("AGENTDRILL FULL TOOL TRACING TEST")
    print("=" * 65)
    print("Verifier passed:", result["passed"])
    print("Tool events recorded:", len(events))

    for event in events:
        print()
        print(json.dumps(event, indent=2, default=str))

    print()
    print("Unauthorized refund attempt captured: YES")
    print("Tracing test: PASS")


if __name__ == "__main__":
    main()
