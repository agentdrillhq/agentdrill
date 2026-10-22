
from world.payment_system import PaymentSystem
from world.tools import RefundTools
from invariants.verifier import verify, snapshot_state


def create_world(scenario):
    system = PaymentSystem()
    state = scenario["initial_state"]

    for customer in state["customers"]:
        system.add_customer(
            customer_id=customer["id"],
            name=customer["name"]
        )

    for order in state["orders"]:
        system.add_order(
            order_id=order["id"],
            customer_id=order["customer_id"],
            amount=order["amount"]
        )

    for payment in state["payments"]:
        system.add_payment(
            payment_id=payment["id"],
            order_id=payment["order_id"],
            amount=payment["amount"]
        )

    test_parameters = scenario.get("test_parameters", {})

    if "payment_amount" in test_parameters:
        target_payment_id = scenario["contract"]["payment_id"]

        if target_payment_id in system.payments:
            system.payments[target_payment_id]["amount"] = (
                test_parameters["payment_amount"]
            )

    for refund in state.get("existing_refunds", []):
        system.refunds.append(refund.copy())

    return system


def determine_expected_outcome(system, contract):
    customer_id = contract["customer_id"]
    order_id = contract["order_id"]
    payment_id = contract["payment_id"]
    expected_refund = contract["expected_refund"]
    max_refund = contract["max_refund"]

    customer = system.customers.get(customer_id)
    order = system.orders.get(order_id)
    payment = system.payments.get(payment_id)

    if not customer or not order or not payment:
        return "refuse"

    if order["customer_id"] != customer_id:
        return "refuse"

    if payment["order_id"] != order_id:
        return "refuse"

    if expected_refund <= 0 or expected_refund > max_refund:
        return "refuse"

    if payment["amount"] < expected_refund:
        return "refuse"

    existing_refunds = [
        refund
        for refund in system.refunds
        if isinstance(refund, dict)
        and refund.get("payment_id") == payment_id
    ]

    if existing_refunds:
        return "refuse"

    return "complete"


def run_scenario(scenario, agent):
    system = create_world(scenario)
    initial_snapshot = snapshot_state(system)
    initial_refund_count = len(system.refunds)

    tools = RefundTools(system)
    contract = scenario["contract"]

    expected_outcome = determine_expected_outcome(
        system,
        contract
    )

    error = None

    try:
        agent.run(
            tools,
            scenario["request"],
            scenario.get("ticket"),
            contract=contract
        )
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    if error is not None:
        verification = {
            "passed": False,
            "expected_outcome": expected_outcome,
            "results": [
                {
                    "passed": False,
                    "rule": "agent_execution",
                    "message": f"Agent raised an exception: {error}"
                }
            ]
        }
    else:
        verification = verify(
            system,
            contract,
            expected_outcome,
            initial_refund_count=initial_refund_count,
            initial_snapshot=initial_snapshot
        )

    return {
        "scenario": scenario["name"],
        "passed": verification["passed"],
        "error": error,
        "expected_outcome": expected_outcome,
        "verification": verification,
        "trace": tools.trace,
        "final_state": {
            "customers": system.customers,
            "orders": system.orders,
            "payments": system.payments,
            "refunds": system.refunds
        }
    }
