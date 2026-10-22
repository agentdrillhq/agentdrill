
import unittest

from agents.refund_agents import (
    DefensiveAgent,
    BadAgent,
    WrongOrderAgent,
    TicketDrivenAgent,
)

from scenarios.refund_scenarios import (
    standard_refund_scenario,
    duplicate_refund_scenario,
)

from scenarios.generators import generate_combined_scenarios
from scenarios.runner import run_scenario


class CrashingAgent:
    """Deliberately crashes to test AgentDrill error handling."""

    def run(self, tools, request, ticket=None, contract=None):
        raise RuntimeError("Intentional test crash")


class StateTamperingAgent:
    """Modifies customer data without authorization."""

    def run(self, tools, request, ticket=None, contract=None):
        tools.system.customers["C001"]["name"] = "Tampered Name"


class RefundHistoryTamperingAgent:
    """Deletes existing refund history."""

    def run(self, tools, request, ticket=None, contract=None):
        tools.system.refunds.clear()


class MalformedRefundAgent:
    """Creates a refund record with a missing amount."""

    def run(self, tools, request, ticket=None, contract=None):
        tools.system.refunds.append({
            "payment_id": "P100"
        })


class AgentDrillSelfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scenarios = {
            scenario["name"]: scenario
            for scenario in generate_combined_scenarios()
        }

    def test_safe_agent_completes_standard_refund(self):
        result = run_scenario(
            standard_refund_scenario(),
            DefensiveAgent()
        )

        self.assertTrue(result["passed"], result["verification"])
        self.assertIsNone(result["error"])
        self.assertEqual(len(result["final_state"]["refunds"]), 1)

    def test_safe_agent_refuses_duplicate_refund(self):
        result = run_scenario(
            duplicate_refund_scenario(),
            DefensiveAgent()
        )

        self.assertTrue(result["passed"], result["verification"])
        self.assertEqual(result["expected_outcome"], "refuse")

    def test_duplicate_refund_agent_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            BadAgent()
        )

        self.assertFalse(result["passed"])
        self.assertIsNone(result["error"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn("no_duplicate_refund", failed_rules)

    def test_wrong_order_agent_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            WrongOrderAgent()
        )

        self.assertFalse(result["passed"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn(
            "refund_matches_contract_payment",
            failed_rules,
            f"Wrong-order refund was not detected: {failed_rules}"
        )

    def test_prompt_injection_agent_is_detected(self):
        scenario = self.scenarios["standard_refund_ticket_injection"]

        result = run_scenario(
            scenario,
            TicketDrivenAgent()
        )

        self.assertFalse(result["passed"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertTrue(
            {
                "refund_matches_contract_payment",
                "refund_matches_expected_amount",
                "refund_amounts_valid",
                "refund_relationships_valid",
            }.intersection(failed_rules),
            f"Injection was not detected: {failed_rules}"
        )

    def test_invalid_contract_is_safely_refused(self):
        scenario = self.scenarios["contract_zero_refund"]

        result = run_scenario(
            scenario,
            DefensiveAgent()
        )

        self.assertTrue(result["passed"], result["verification"])
        self.assertEqual(result["expected_outcome"], "refuse")
        self.assertEqual(result["final_state"]["refunds"], [])

    def test_crashing_agent_is_not_a_pass(self):
        result = run_scenario(
            standard_refund_scenario(),
            CrashingAgent()
        )

        self.assertFalse(result["passed"])
        self.assertIsNotNone(result["error"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn("agent_execution", failed_rules)

    def test_all_generated_scenarios_have_names(self):
        scenarios = generate_combined_scenarios()
        names = [scenario["name"] for scenario in scenarios]

        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(names))

    def test_customer_state_tampering_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            StateTamperingAgent()
        )

        self.assertFalse(result["passed"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn("customers_unchanged", failed_rules)

    def test_existing_refund_history_cannot_be_deleted(self):
        result = run_scenario(
            duplicate_refund_scenario(),
            RefundHistoryTamperingAgent()
        )

        self.assertFalse(result["passed"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn("refund_history_preserved", failed_rules)

    def test_malformed_refund_record_is_detected(self):
        result = run_scenario(
            standard_refund_scenario(),
            MalformedRefundAgent()
        )

        self.assertFalse(result["passed"])

        failed_rules = {
            item["rule"]
            for item in result["verification"]["results"]
            if not item["passed"]
        }

        self.assertIn("refund_record_structure", failed_rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
