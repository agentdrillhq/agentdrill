from world.payment_system import PaymentSystem
from world.tools import RefundTools
from invariants.verifier import verify
from agents.refund_agents import (
    CarefulAgent,
    BadAgent,
    WrongAmountAgent,
    WrongOrderAgent
)
from invariants.contracts import REFUND_CONTRACT

def create_world():
    system = PaymentSystem()

    system.add_customer(
        customer_id="C001",
        name="Rahul"
    )

    system.add_order(
        order_id="O100",
        customer_id="C001",
        amount=5000
    )

    system.add_payment(
        payment_id="P100",
        order_id="O100",
        amount=5000
    )

    system.add_customer(
        customer_id="C002",
        name="Arjun"
    )

    system.add_order(
        order_id="O200",
        customer_id="C002",
        amount=3000
    )

    system.add_payment(
        payment_id="P200",
        order_id="O200",
        amount=3000
    )

    return system


print("========== CAREFUL AGENT ==========")

system = create_world()
tools = RefundTools(system)

agent = CarefulAgent()
agent.run(tools)

print("Refunds:")
print(system.refunds)

print()

print("Trace:")
for event in tools.trace:
    print(event)


print()
result = verify(system, REFUND_CONTRACT)

print()
print("Verification:")
print(result)
print("========== BAD AGENT ==========")

system = create_world()
tools = RefundTools(system)

agent = BadAgent()
agent.run(tools)

print("Refunds:")
print(system.refunds)

print()

print("Trace:")
for event in tools.trace:
    print(event)

result = verify(system, REFUND_CONTRACT)

print()
print("Verification:")
print(result)


print()
print("========== WRONG AMOUNT AGENT ==========")

system = PaymentSystem()

system.add_customer("C001", "Rahul")
system.add_order("O100", "C001", 5000)
system.add_payment("P100", "O100", 5000)

tools = RefundTools(system)

agent = WrongAmountAgent()
agent.run(tools)

print("Refunds:")
print(system.refunds)

print()
print("Trace:")
for item in tools.trace:
    print(item)

result = verify(system, REFUND_CONTRACT)

print()
print("Verification:")
print(result)


print()
print("========== WRONG ORDER AGENT ==========")

system = create_world()
tools = RefundTools(system)

agent = WrongOrderAgent()
agent.run(tools)

print("Refunds:")
print(system.refunds)

print()
print("Trace:")
for item in tools.trace:
    print(item)

result = verify(system, REFUND_CONTRACT)

print()
print("Verification:")
print(result)