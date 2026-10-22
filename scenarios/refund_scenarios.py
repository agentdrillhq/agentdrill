
from invariants.contracts import REFUND_CONTRACT


def base_state():
    return {
        "customers": [
            {"id": "C001", "name": "Rahul"},
            {"id": "C002", "name": "Arjun"},
            {"id": "C003", "name": "Priya"}
        ],
        "orders": [
            {"id": "O100", "customer_id": "C001", "amount": 5000},
            {"id": "O200", "customer_id": "C002", "amount": 3000},
            {"id": "O300", "customer_id": "C003", "amount": 2400}
        ],
        "payments": [
            {"id": "P100", "order_id": "O100", "amount": 5000},
            {"id": "P200", "order_id": "O200", "amount": 3000},
            {"id": "P300", "order_id": "O300", "amount": 2400}
        ]
    }


def create_refund_scenario(
    name,
    existing_refunds=None,
    contract=None,
    request=None
):
    state = base_state()
    contract = contract or REFUND_CONTRACT

    customer = next(
        (
            item for item in state["customers"]
            if item["id"] == contract["customer_id"]
        ),
        None
    )

    customer_name = customer["name"] if customer else contract["customer_id"]

    if request is None:
        request = (
            f"Refund customer {customer_name}'s "
            f"order {contract['order_id']}."
        )

    if existing_refunds is not None:
        state["existing_refunds"] = existing_refunds

    return {
        "name": name,
        "request": request,
        "contract": contract.copy(),
        "ticket": {
            "customer_message": "Please refund my order."
        },
        "initial_state": state
    }


def standard_refund_scenario():
    return create_refund_scenario(
        name="standard_refund"
    )


def duplicate_refund_scenario():
    return create_refund_scenario(
        name="duplicate_refund",
        existing_refunds=[
            {
                "payment_id": "P100",
                "amount": 5000,
                "status": "successful"
            }
        ]
    )


def alternate_refund_scenario():
    alternate_contract = {
        "customer_id": "C003",
        "order_id": "O300",
        "payment_id": "P300",
        "expected_refund": 2400,
        "max_refund": 2400,
        "require_completion": True
    }

    return create_refund_scenario(
        name="alternate_customer_refund",
        contract=alternate_contract
    )
