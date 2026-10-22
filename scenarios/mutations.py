def mutate_payment_amount(scenario, amount):
    mutated = {
        **scenario,
        "initial_state": {
            **scenario["initial_state"],
            "payments": [
                {
                    **payment,
                    "amount": amount
                }
                if payment["id"] == "P100"
                else payment
                for payment in scenario["initial_state"]["payments"]
            ]
        }
    }

    mutated["name"] = f"{scenario['name']}_payment_{amount}"

    return mutated


def mutate_payment_order(scenario, order_id):
    mutated = {
        **scenario,
        "initial_state": {
            **scenario["initial_state"],
            "payments": [
                {
                    **payment,
                    "order_id": order_id
                }
                if payment["id"] == "P100"
                else payment
                for payment in scenario["initial_state"]["payments"]
            ]
        }
    }

    mutated["name"] = f"{scenario['name']}_order_{order_id}"

    return mutated


def apply_mutations(scenario, mutations):
    mutated = scenario

    for mutation in mutations:
        mutated = mutation(mutated)

    return mutated


def mutate_ticket_message(scenario, message):
    mutated = {
        **scenario,
        "ticket": {
            **scenario["ticket"],
            "customer_message": message
        }
    }

    mutated["name"] = f"{scenario['name']}_ticket_injection"

    return mutated

def mutate_ticket_message(scenario, message):
    mutated = {
        **scenario,
        "ticket": {
            **scenario["ticket"],
            "customer_message": message
        }
    }

    mutated["name"] = f"{scenario['name']}_ticket_injection"

    return mutated

def set_expected_outcome(scenario, outcome):
    mutated = {
        **scenario,
        "expected_outcome": outcome
    }

    return mutated