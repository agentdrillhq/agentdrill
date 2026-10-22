
import copy
import time
from datetime import datetime, timezone


class ToolRegistry:
    """
    Generic tool registry with execution tracing.

    Developers register Python functions.
    Agents call them through the registry.

    Every invocation records:
      - tool name
      - arguments
      - result or exception
      - state before and after
      - whether state changed
      - execution duration

    This is an observability wrapper, not a security sandbox.
    """

    def __init__(self, snapshot=None):
        self._tools = {}
        self._snapshot = snapshot
        self.events = []

    def register(self, name, function):
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError("Tool name must be a valid identifier")

        if not callable(function):
            raise TypeError("Registered tool must be callable")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = function

    def _capture_state(self):
        if self._snapshot is None:
            return None
        return copy.deepcopy(self._snapshot())

    def call(self, name, **kwargs):
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        started = time.perf_counter()
        before = self._capture_state()

        event = {
            "sequence": len(self.events) + 1,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "tool": name,
            "arguments": copy.deepcopy(kwargs),
            "status": "ATTEMPTED",
            "result": None,
            "error": None,
            "state_changed": False,
            "state_before": before,
            "state_after": None,
            "duration_seconds": None,
        }

        # Record intent before executing the function.
        self.events.append(event)

        try:
            result = self._tools[name](**kwargs)
            event["result"] = copy.deepcopy(result)
            event["status"] = "SUCCESS"

            return copy.deepcopy(result)

        except Exception as exc:
            event["status"] = "ERROR"
            event["error"] = (
                f"{type(exc).__name__}: {exc}"
            )
            raise

        finally:
            after = self._capture_state()

            event["state_after"] = after

            if self._snapshot is not None:
                event["state_changed"] = before != after

            event["duration_seconds"] = round(
                time.perf_counter() - started,
                6,
            )

    def __getattr__(self, name):
        """
        Allow tools.transfer_money(...)
        instead of tools.call("transfer_money", ...).
        """
        if name.startswith("_"):
            raise AttributeError(name)

        if name not in self._tools:
            raise AttributeError(
                f"Tool not registered: {name}"
            )

        def invoke(**kwargs):
            return self.call(name, **kwargs)

        return invoke

    def available_tools(self):
        return list(self._tools.keys())
