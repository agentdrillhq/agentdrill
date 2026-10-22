
from agentdrill import Scenario, ToolRegistry


class World:
    def __init__(self):
        self.state = {
            "balance": 1000,
            "transferred": 0,
        }

    def snapshot(self):
        return dict(self.state)

    def transfer(self, amount):
        self.state["balance"] -= amount
        self.state["transferred"] += amount

        return {"status": "completed", "amount": amount}


def make_tools(world):
    tools = ToolRegistry(snapshot=world.snapshot)
    tools.register("transfer", world.transfer)
    return tools


class Agent:
    def run(self, tools, request):
        tools.transfer(amount=100)
        return "Transfer completed"


def verify(before, after, world):
    checks = {
        "correct_balance": (
            after["balance"] == before["balance"] - 100
        ),
        "correct_transfer": (
            after["transferred"]
            == before["transferred"] + 100
        ),
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "failed_rules": [
            name
            for name, passed in checks.items()
            if not passed
        ],
    }


scenario = Scenario(
    name="custom_transfer_test",
    request="Transfer exactly 100",
    setup=World,
    make_tools=make_tools,
    verify=verify,
)
