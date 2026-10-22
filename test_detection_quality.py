
import unittest

from agents.refund_agents import DefensiveAgent
from agents.adversarial_agents import (
    OverRefundAgent,
    PartialRefundAgent,
    DuplicateRefundAgent,
    CustomerTamperingAgent,
)
from scenarios.refund_scenarios import standard_refund_scenario
from scenarios.runner import run_scenario


class DetectionQualityTests(unittest.TestCase):

    def test_safe_agent_passes_valid_refund(self):
        result = run_scenario(
            standard_refund_scenario(),
            DefensiveAgent(),
        )

        self.assertTrue(result["passed"], result["verification"])

    def test_over_refund_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            OverRefundAgent(),
        )

        self.assertFalse(
            result["passed"],
            "AgentDrill failed to detect an excessive refund.",
        )

    def test_partial_refund_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            PartialRefundAgent(),
        )

        self.assertFalse(
            result["passed"],
            "AgentDrill failed to detect an incorrect refund amount.",
        )

    def test_duplicate_refund_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            DuplicateRefundAgent(),
        )

        self.assertFalse(
            result["passed"],
            "AgentDrill failed to detect duplicate refunds.",
        )

    def test_customer_tampering_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            CustomerTamperingAgent(),
        )

        self.assertFalse(
            result["passed"],
            "AgentDrill failed to detect customer data tampering.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

