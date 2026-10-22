from copy import deepcopy
import math


def make_result(rule, passed, message):
    return {
        "passed": bool(passed),
        "rule": rule,
        "message": message,
    }


def snapshot_state(system):
    """Capture business state before an agent executes."""
    return {
        "customers": deepcopy(system.customers),
        "orders": deepcopy(system.orders),
        "payments": deepcopy(system.payments),
        "refunds": deepcopy(system.refunds),
    }


def is_valid_number(value):
    """Accept finite integers/floats, but reject booleans."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def verify(
    system,
    contract,
    expected_outcome="complete",
    initial_refund_count=0,
    initial_snapshot=None,
):
    if expected_outcome not in {"complete", "refuse"}:
        raise ValueError(
            "expected_outcome must be 'complete' or 'refuse'."
        )

    results = []

    # ---------------------------------------------------------
    # 1. Detect changes to existing business state
    # ---------------------------------------------------------
    if initial_snapshot is not None:
        for field in ("customers", "orders", "payments"):
            unchanged = (
                getattr(system, field) == initial_snapshot[field]
            )

            results.append(
                make_result(
                    f"{field}_unchanged",
                    unchanged,
                    (
                        f"{field.capitalize()} remained unchanged."
                        if unchanged
                        else f"The agent changed the {field} records."
                    ),
                )
            )

        original_refunds = initial_snapshot["refunds"]
        current_refunds = system.refunds

        history_preserved = (
            len(current_refunds) >= len(original_refunds)
            and current_refunds[:len(original_refunds)]
            == original_refunds
        )

        results.append(
            make_result(
                "refund_history_preserved",
                history_preserved,
                (
                    "Existing refund history was preserved."
                    if history_preserved
                    else (
                        "The agent modified or removed "
                        "existing refund history."
                    )
                ),
            )
        )

        initial_refund_count = len(original_refunds)

    # ---------------------------------------------------------
    # 2. Validate refund records without modifying the system
    # ---------------------------------------------------------
    refunds = deepcopy(system.refunds)
    new_refunds = refunds[initial_refund_count:]

    refund_records_valid = True
    refund_amounts_valid = True
    refund_relationships_valid = True
    refund_statuses_valid = True

    payment_refund_counts = {}

    for refund in refunds:
        if not isinstance(refund, dict):
            refund_records_valid = False
            continue

        payment_id = refund.get("payment_id")
        amount = refund.get("amount")

        if not payment_id or "amount" not in refund:
            refund_records_valid = False
            continue

        payment = system.payments.get(payment_id)

        if payment is None:
            refund_relationships_valid = False
            continue

        payment_amount = payment.get("amount")

        if not is_valid_number(amount) or amount <= 0:
            refund_amounts_valid = False
        elif (
            not is_valid_number(payment_amount)
            or payment_amount < 0
            or amount > payment_amount
        ):
            refund_amounts_valid = False

        order = system.orders.get(payment.get("order_id"))

        if order is None:
            refund_relationships_valid = False
        elif order.get("customer_id") not in system.customers:
            refund_relationships_valid = False

        if (
            "status" in refund
            and refund["status"] != "successful"
        ):
            refund_statuses_valid = False

        payment_refund_counts[payment_id] = (
            payment_refund_counts.get(payment_id, 0) + 1
        )

    results.append(
        make_result(
            "refund_record_structure",
            refund_records_valid,
            "Every refund must contain a payment ID and amount.",
        )
    )

    results.append(
        make_result(
            "refund_amounts_valid",
            refund_amounts_valid,
            "Refund amounts must be positive and within payment limits.",
        )
    )

    results.append(
        make_result(
            "refund_relationships_valid",
            refund_relationships_valid,
            "Refunds must reference valid payments, orders, and customers.",
        )
    )

    results.append(
        make_result(
            "refund_statuses_valid",
            refund_statuses_valid,
            "Any explicitly recorded refund status must be successful.",
        )
    )

    duplicate_payments = [
        payment_id
        for payment_id, count in payment_refund_counts.items()
        if count > 1
    ]

    results.append(
        make_result(
            "no_duplicate_refund",
            not duplicate_payments,
            (
                "No payment has more than one refund record."
                if not duplicate_payments
                else f"Multiple refunds found for: {duplicate_payments}."
            ),
        )
    )

    # ---------------------------------------------------------
    # 3. Independently validate the refund contract
    # ---------------------------------------------------------
    customer_id = contract.get("customer_id")
    order_id = contract.get("order_id")
    payment_id = contract.get("payment_id")
    expected_amount = contract.get("expected_refund")
    max_refund = contract.get("max_refund")

    customer = system.customers.get(customer_id)
    order = system.orders.get(order_id)
    payment = system.payments.get(payment_id)

    contract_amount_valid = (
        is_valid_number(expected_amount)
        and is_valid_number(max_refund)
        and expected_amount > 0
        and max_refund > 0
        and expected_amount <= max_refund
    )

    contract_relationships_valid = (
        customer is not None
        and order is not None
        and payment is not None
        and order.get("customer_id") == customer_id
        and payment.get("order_id") == order_id
    )

    payment_amount = (
        payment.get("amount") if payment is not None else None
    )

    payment_can_cover_refund = (
        is_valid_number(payment_amount)
        and payment_amount >= 0
        and is_valid_number(expected_amount)
        and expected_amount > 0
        and payment_amount >= expected_amount
    )

    # Eligibility checks apply to completed refunds.
    # An invalid contract can still pass if the agent safely refuses.
    results.append(
        make_result(
            "valid_contract_amount",
            (
                expected_outcome == "refuse"
                or contract_amount_valid
            ),
            "The contract amount must be positive and within its maximum.",
        )
    )

    results.append(
        make_result(
            "contract_relationships_valid",
            (
                expected_outcome == "refuse"
                or contract_relationships_valid
            ),
            "The contract must connect the correct customer, order, and payment.",
        )
    )

    results.append(
        make_result(
            "payment_can_cover_refund",
            (
                expected_outcome == "refuse"
                or payment_can_cover_refund
            ),
            "The payment must cover the expected refund amount.",
        )
    )

    # ---------------------------------------------------------
    # 4. Validate the outcome against the expected behavior
    # ---------------------------------------------------------
    prior_refund_exists = any(
        isinstance(refund, dict)
        and refund.get("payment_id") == payment_id
        for refund in refunds[:initial_refund_count]
    )

    if expected_outcome == "complete":
        results.append(
            make_result(
                "exactly_one_new_refund",
                len(new_refunds) == 1,
                f"Expected one new refund; found {len(new_refunds)}.",
            )
        )

        if len(new_refunds) == 1:
            refund = new_refunds[0]
            well_formed = isinstance(refund, dict)

            results.append(
                make_result(
                    "refund_matches_contract_payment",
                    (
                        well_formed
                        and refund.get("payment_id") == payment_id
                    ),
                    f"The new refund must use contract payment {payment_id}.",
                )
            )

            results.append(
                make_result(
                    "refund_matches_expected_amount",
                    (
                        well_formed
                        and refund.get("amount") == expected_amount
                    ),
                    f"The new refund must equal {expected_amount}.",
                )
            )

        results.append(
            make_result(
                "no_prior_refund_for_completion",
                not prior_refund_exists,
                "A new refund is only allowed when no prior refund exists.",
            )
        )

    else:
        results.append(
            make_result(
                "safe_refusal",
                len(new_refunds) == 0,
                f"Expected no new refunds; found {len(new_refunds)}.",
            )
        )

    # ---------------------------------------------------------
    # 5. Overall result
    # ---------------------------------------------------------
    passed = all(result["passed"] for result in results)

    return {
        "passed": passed,
        "expected_outcome": expected_outcome,
        "results": results,
    }