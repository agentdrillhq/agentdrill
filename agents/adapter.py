
import importlib
import inspect


class CustomAgentAdapter:
    """
    Adapter for a developer-supplied Python function.

    Required interface:
        run_agent(tools, request, ticket=None, contract=None)
    """

    def __init__(self, target):
        if ":" not in target:
            raise ValueError(
                "Invalid agent target. Use module:function, "
                "for example custom_agent:run_agent"
            )

        module_name, function_name = target.split(":", 1)

        if not module_name or not function_name:
            raise ValueError(
                "Invalid agent target. Use module:function."
            )

        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            raise ImportError(
                f"Could not import module '{module_name}': {exc}"
            ) from exc

        agent_function = getattr(module, function_name, None)

        if not callable(agent_function):
            raise TypeError(
                f"'{target}' does not identify a callable function."
            )

        try:
            signature = inspect.signature(agent_function)
            signature.bind(
                object(),
                "test request",
                ticket=None,
                contract={}
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"Incompatible agent interface for '{target}'. "
                "Expected a function accepting "
                "run_agent(tools, request, ticket=None, contract=None)."
            ) from exc

        self.agent_function = agent_function
        self.agent_name = target

    def run(self, tools, request, ticket=None, contract=None):
        return self.agent_function(
            tools,
            request,
            ticket=ticket,
            contract=contract
        )
