class PaymentSystem:
    def __init__(self):
        self.customers = {}
        self.orders = {}
        self.payments = {}
        self.refunds = []

    def add_customer(self, customer_id, name):
        self.customers[customer_id] = {
            "id": customer_id,
            "name": name
        }

    def add_order(self, order_id, customer_id, amount):
        self.orders[order_id] = {
            "id": order_id,
            "customer_id": customer_id,
            "amount": amount
        }

    def add_payment(self, payment_id, order_id, amount):
        self.payments[payment_id] = {
            "id": payment_id,
            "order_id": order_id,
            "amount": amount,
            "status": "paid"
        }

    def issue_refund(self, payment_id, amount):
        payment = self.payments[payment_id]

        refund = {
            "payment_id": payment_id,
            "amount": amount,
            "status": "successful"
        }

        self.refunds.append(refund)

        return refund