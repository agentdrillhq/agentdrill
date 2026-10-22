
# AgentDrill

**Test what your AI agent actually changes, not just what it says.**

AgentDrill is an open-source Python testing framework for
tool-using AI agents.

It runs agents against simulated environments and independently
verifies resulting business-state changes.

Instead of asking only whether an AI agent produced a correct
response, AgentDrill checks whether its actions respected
business rules.

## Why AgentDrill?

An AI agent might:

- Transfer the wrong amount of money
- Issue a duplicate refund
- Modify an unauthorized customer field
- Reserve incorrect inventory quantities
- Fail to complete a legitimate operation

AgentDrill helps developers detect these problems during testing,
before connecting agents to real business systems.

## Features

- Bring your own Python agent
- Define custom simulated environments
- Register and trace Python tool calls
- Inspect state before and after execution
- Define custom business-rule verification
- Detect incorrect and incomplete actions
- Generate structured JSON reports
- Run tests through a Python API or CLI

## Installation

Requires Python 3.10 or later.

Clone the repository and install:

    git clone https://github.com/agentdrillhq/agentdrill.git
    cd agentdrill
    python -m pip install -e .

The repository URL will be updated after the GitHub repository is created.

## Quick Start

Run the bundled generic example:

    agentdrill custom --file examples/quickstart.py

Expected output:

    AGENTDRILL - CUSTOM AGENT EVALUATION

    Scenario: custom_transfer_test
    Agent: Agent

    Result: PASS
    Failed rules: []
    Tool events: 1

## Python API

Import the public interfaces:

    from agentdrill import Scenario, evaluate, ToolRegistry

Define a scenario:

    scenario = Scenario(
        name="my_workflow",
        request="Perform the authorized action",
        setup=MyWorld,
        make_tools=make_tools,
        verify=my_verifier,
    )

Evaluate an agent:

    result = evaluate(MyAgent(), scenario)

    print(result["passed"])
    print(result["verification"])

The developer supplies the world, tools, agent, and verification rules.

## Required Interfaces

### Environment

The environment implements snapshot():

    class MyWorld:
        def snapshot(self):
            return {"value": 10}

### Agent

The agent implements run(tools, request):

    class MyAgent:
        def run(self, tools, request):
            return tools.my_action(value=5)

### Verification

The verifier receives before, after, and world:

    def my_verifier(before, after, world):
        passed = after["value"] == 5

        return {
            "passed": passed,
            "failed_rules": [] if passed else ["wrong_value"],
        }

## Generic Tool Tracing

Register tools through ToolRegistry:

    registry = ToolRegistry(snapshot=world.snapshot)

    registry.register(
        "my_action",
        world.my_action,
    )

    registry.call("my_action", value=5)

    print(registry.events)

The registry records:

- Tool name and arguments
- Execution result or exception
- State before and after execution
- Whether the state changed
- Execution duration

## CLI

Run a custom scenario:

    agentdrill custom --file my_test.py

The Python file must define:

- scenario: an AgentDrill Scenario instance
- Agent: a Python class implementing run(tools, request)

List bundled refund scenarios:

    agentdrill list

Test a compatible refund agent:

    agentdrill test --agent examples/my_agent.py

The generic Python API is domain-independent.
The bundled refund CLI remains a domain-specific example.

## Examples

The repository includes demonstrations for:

- Refund workflows
- CRM customer updates
- Inventory management
- Banking-style transfers
- Custom business rules

## Limitations

AgentDrill is currently an experimental alpha.

- Agent code runs in the same Python process.
- It is not a security sandbox.
- Custom simulations and verification rules are developer-defined.
- Tool tracing only covers calls routed through the tracing adapter.
- Arbitrary third-party agent frameworks are not automatically supported.
- Automatic adversarial scenario generation is not yet available.
- Production reliability has not been established.

Do not use the current execution model to run untrusted Python
code or connect tests directly to irreversible production actions.

## Project Status

Version 0.7.0 — Alpha.

We are looking for developers building tool-using AI agents who
want to test business-state correctness.

Feedback and reproducible failure cases are especially valuable.

## License

MIT.
