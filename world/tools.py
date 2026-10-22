from world.payment_system import PaymentSystem


class RefundTools:
    def __init__(self, system: PaymentSystem):
        self.system = system
        self.trace = []

    def _record(self, tool, arguments, result):
        self.trace.append({
            "tool": tool,
            "arguments": arguments,
            "result": result
        })

    def lookup_customer(self, customer_id):
        result = self.system.customers.get(customer_id)

        self._record(
            "lookup_customer",
            {"customer_id": customer_id},
            result
        )

        return result

    def lookup_order(self, order_id):
        result = self.system.orders.get(order_id)

        self._record(
            "lookup_order",
            {"order_id": order_id},
            result
        )

        return result

    def lookup_payment(self, payment_id):
        result = self.system.payments.get(payment_id)

        self._record(
            "lookup_payment",
            {"payment_id": payment_id},
            result
        )

        return result

    def issue_refund(self, payment_id, amount):
        result = self.system.issue_refund(payment_id, amount)

        self._record(
            "issue_refund",
            {
                "payment_id": payment_id,
                "amount": amount
            },
            result
        )

        return result
    
    def lookup_refunds(self, payment_id):
        result = [
            refund
            for refund in self.system.refunds
            if refund["payment_id"] == payment_id
        ]

        self._record(
            "lookup_refunds",
            {"payment_id": payment_id},
            result
        )

        return result
    