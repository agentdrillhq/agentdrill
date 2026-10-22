
from agents.ollama_agent import OllamaRefundAgent
from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


def main():
    scenarios = generate_combined_scenarios()

    scenario = next(
        s for s in scenarios
        if s["name"] == "standard_refund_payment_5001"
    )

    agent = OllamaRefundAgent(model="qwen3:4b")

    print("=" * 60)
    print("AGENTDRILL - REAL LOCAL AI AGENT TEST")
    print("=" * 60)

    print("Model:", agent.model)
    print("Scenario:", scenario["name"])
    print()

    result = run_scenario(scenario, agent)

    print("Passed:", result["passed"])
    print("Expected outcome:", result.get("expected_outcome"))
    print("Error:", result.get("error"))
    print()
    print("Verification:")
    print(json_pretty(result.get("verification")))
    print()
    print("Tool trace:")
    print(json_pretty(result.get("trace")))
    print()
    print("Final state:")
    print(json_pretty(result.get("final_state")))


def json_pretty(value):
    import json
    return json.dumps(value, indent=2, default=str)


if __name__ == "__main__":
    main()
