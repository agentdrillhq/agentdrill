
class CarefulAgent:

    def run(self, tools, request, ticket=None, contract=None):
        if not contract:
            return

        customer = tools.lookup_customer(contract["customer_id"])
        order = tools.lookup_order(contract["order_id"])
        payment = tools.lookup_payment(contract["payment_id"])

        if not customer or not order or not payment:
            return

        if order["customer_id"] != customer["id"]:
            return

        if payment["order_id"] != order["id"]:
            return

        existing_refunds = tools.lookup_refunds(payment["id"])

        refunded_amount = sum(
            refund["amount"]
            for refund in existing_refunds
        )

        remaining_amount = (
            order["amount"] - refunded_amount
        )

        if remaining_amount <= 0:
            return

        tools.issue_refund(
            payment_id=payment["id"],
            amount=remaining_amount
        )


class BadAgent:

    def run(self, tools, request, ticket=None, contract=None):
        tools.issue_refund(
            payment_id="P100",
            amount=5000
        )

        tools.issue_refund(
            payment_id="P100",
            amount=5000
        )


class WrongAmountAgent:

    def run(self, tools, request, ticket=None, contract=None):
        payment_id = (
            contract["payment_id"] if contract else "P100"
        )

        tools.issue_refund(
            payment_id=payment_id,
            amount=6000
        )


class WrongOrderAgent:

    def run(self, tools, request, ticket=None, contract=None):
        # Intentionally selects the wrong customer's order.
        customer = tools.lookup_customer("C002")
        order = tools.lookup_order("O200")
        payment = tools.lookup_payment("P200")

        if not order or not payment:
            return

        tools.issue_refund(
            payment_id=payment["id"],
            amount=order["amount"]
        )


class PartialRefundAgent:

    def run(self, tools, request, ticket=None, contract=None):
        payment_id = (
            contract["payment_id"] if contract else "P100"
        )

        tools.issue_refund(
            payment_id=payment_id,
            amount=1000
        )


class TicketDrivenAgent:

    def run(self, tools, request, ticket=None, contract=None):
        if not contract:
            return

        customer = tools.lookup_customer(contract["customer_id"])
        order = tools.lookup_order(contract["order_id"])
        payment = tools.lookup_payment(contract["payment_id"])

        if not customer or not order or not payment:
            return

        if ticket:
            message = ticket.get("customer_message", "")

            # Intentionally vulnerable to malicious ticket instructions.
            if "50000" in message:
                tools.issue_refund(
                    payment_id=payment["id"],
                    amount=50000
                )
                return

        tools.issue_refund(
            payment_id=payment["id"],
            amount=contract["expected_refund"]
        )


class DefensiveAgent:

    def run(self, tools, request, ticket=None, contract=None):
        if not contract:
            return

        customer_id = contract["customer_id"]
        order_id = contract["order_id"]
        payment_id = contract["payment_id"]
        expected_refund = contract["expected_refund"]
        max_refund = contract["max_refund"]

        customer = tools.lookup_customer(customer_id)
        order = tools.lookup_order(order_id)
        payment = tools.lookup_payment(payment_id)

        if not customer or not order or not payment:
            return

        if order["customer_id"] != customer_id:
            return

        if payment["order_id"] != order_id:
            return

        if payment["amount"] < expected_refund:
            return

        if expected_refund <= 0 or expected_refund > max_refund:
            return

        existing_refunds = tools.lookup_refunds(payment_id)

        # Do not issue another refund if one already exists.
        if existing_refunds:
            return

        tools.issue_refund(
            payment_id=payment_id,
            amount=expected_refund
        )
