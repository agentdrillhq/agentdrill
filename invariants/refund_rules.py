def no_duplicate_refund(system):
    seen_payments = set()

    for refund in system.refunds:
        payment_id = refund["payment_id"]

        if payment_id in seen_payments:
            return {
                "passed": False,
                "rule": "no_duplicate_refund",
                "message": f"Payment {payment_id} was refunded more than once."
            }

        seen_payments.add(payment_id)

    return {
        "passed": True,
        "rule": "no_duplicate_refund",
        "message": "No duplicate refunds detected."
    }


def refund_not_exceed_payment(system):
    for refund in system.refunds:
        payment_id = refund["payment_id"]
        refund_amount = refund["amount"]

        payment = system.payments.get(payment_id)

        if payment is None:
            return {
                "passed": False,
                "rule": "refund_not_exceed_payment",
                "message": f"Payment {payment_id} does not exist."
            }

        if refund_amount > payment["amount"]:
            return {
                "passed": False,
                "rule": "refund_not_exceed_payment",
                "message": (
                    f"Refund of {refund_amount} exceeds "
                    f"payment amount of {payment['amount']}."
                )
            }

    return {
        "passed": True,
        "rule": "refund_not_exceed_payment",
        "message": "All refunds are within the original payment amount."
    }


def refund_matches_order(system):
    for refund in system.refunds:
        payment_id = refund["payment_id"]

        payment = system.payments.get(payment_id)

        if payment is None:
            return {
                "passed": False,
                "rule": "refund_matches_order",
                "message": f"Payment {payment_id} does not exist."
            }

        order_id = payment["order_id"]

        if order_id not in system.orders:
            return {
                "passed": False,
                "rule": "refund_matches_order",
                "message": (
                    f"Payment {payment_id} refers to unknown order {order_id}."
                )
            }

    return {
        "passed": True,
        "rule": "refund_matches_order",
        "message": "All refunds correspond to valid orders."
    }


def refund_matches_customer(system):
    for refund in system.refunds:
        payment_id = refund["payment_id"]

        payment = system.payments.get(payment_id)

        if payment is None:
            return {
                "passed": False,
                "rule": "refund_matches_customer",
                "message": f"Payment {payment_id} does not exist."
            }

        order_id = payment["order_id"]
        order = system.orders.get(order_id)

        if order is None:
            return {
                "passed": False,
                "rule": "refund_matches_customer",
                "message": f"Order {order_id} does not exist."
            }

        customer_id = order["customer_id"]

        if customer_id not in system.customers:
            return {
                "passed": False,
                "rule": "refund_matches_customer",
                "message": (
                    f"Order {order_id} belongs to unknown customer {customer_id}."
                )
            }

    return {
        "passed": True,
        "rule": "refund_matches_customer",
        "message": "All refunds belong to valid customers."
    }


def refund_matches_contract(system, contract):
    expected_customer = contract["customer_id"]
    expected_order = contract["order_id"]
    max_refund = contract["max_refund"]

    for refund in system.refunds:
        payment_id = refund["payment_id"]
        refund_amount = refund["amount"]

        payment = system.payments.get(payment_id)

        if payment is None:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": f"Payment {payment_id} does not exist."
            }

        actual_order = payment["order_id"]

        if actual_order != expected_order:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": (
                    f"Refund was made for order {actual_order}, "
                    f"but expected order is {expected_order}."
                )
            }

        order = system.orders.get(actual_order)

        if order is None:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": f"Order {actual_order} does not exist."
            }

        actual_customer = order["customer_id"]

        if actual_customer != expected_customer:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": (
                    f"Refund belongs to customer {actual_customer}, "
                    f"but expected customer is {expected_customer}."
                )
            }

        if refund_amount > max_refund:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": (
                    f"Refund of {refund_amount} exceeds "
                    f"contract maximum of {max_refund}."
                )
            }
        
        expected_refund = contract["expected_refund"]

        if refund_amount != expected_refund:
            return {
                "passed": False,
                "rule": "refund_matches_contract",
                "message": (
                    f"Refund amount was {refund_amount}, "
                    f"but expected refund is {expected_refund}."
                )
            }

    return {
        "passed": True,
        "rule": "refund_matches_contract",
        "message": "Refund satisfies the task contract."
    }