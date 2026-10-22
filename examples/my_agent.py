
class Agent:
    def run(self, tools, request, ticket=None, contract=None):
        system = tools.system

        customer_id = contract["customer_id"]
        order_id = contract["order_id"]
        payment_id = contract["payment_id"]
        amount = contract["expected_refund"]
        maximum = contract["max_refund"]

        customer = system.customers.get(customer_id)
        order = system.orders.get(order_id)
        payment = system.payments.get(payment_id)

        if not customer or not order or not payment:
            return "REFUSED: Missing record"

        if order["customer_id"] != customer_id:
            return "REFUSED: Wrong customer"

        if payment["order_id"] != order_id:
            return "REFUSED: Wrong order"

        if payment.get("status") != "paid":
            return "REFUSED: Payment not completed"

        if (
            type(amount) not in (int, float)
            or type(maximum) not in (int, float)
            or amount <= 0
            or amount > maximum
        ):
            return "REFUSED: Invalid refund amount"

        payment_amount = payment.get("amount")

        if (
            type(payment_amount) not in (int, float)
            or payment_amount < amount
        ):
            return "REFUSED: Insufficient payment amount"

        existing_refund = any(
            isinstance(refund, dict)
            and refund.get("payment_id") == payment_id
            for refund in system.refunds
        )

        if existing_refund:
            return "REFUSED: Previous refund exists"

        tools.issue_refund(payment_id, amount)

        return "Refund completed"
