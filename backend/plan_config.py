from decimal import Decimal

PLAN_CONFIG = {
    "free": {
        "name": "Gratuito",
        "prices": {"monthly": Decimal("0.00"), "annual": Decimal("0.00")},
        "clients": 5,
        "members": 1,
    },
    "basico": {
        "name": "Essencial",
        "prices": {"monthly": Decimal("79.90"), "annual": Decimal("799.00")},
        "clients": 40,
        "members": 5,
    },
    "profissional": {
        "name": "Profissional",
        "prices": {"monthly": Decimal("149.90"), "annual": Decimal("1499.00")},
        "clients": 100,
        "members": 10,
    },
    "escritorio": {
        "name": "Escritório",
        "prices": {"monthly": Decimal("249.90"), "annual": Decimal("2499.00")},
        "clients": 300,
        "members": 25,
    },
    "business": {
        "name": "Empresarial",
        "prices": {"monthly": Decimal("449.00"), "annual": Decimal("4490.00")},
        "clients": None,
        "members": None,
    },
}

PAID_PLAN_IDS = {"basico", "profissional", "escritorio", "business"}
BILLING_CYCLES = {"monthly", "annual"}


def get_plan_price(plan_id: str, billing_cycle: str = "monthly") -> Decimal:
    plan = PLAN_CONFIG.get(plan_id, PLAN_CONFIG["free"])
    cycle = billing_cycle if billing_cycle in BILLING_CYCLES else "monthly"
    return plan["prices"][cycle]


def get_monthly_equivalent(plan_id: str, billing_cycle: str = "monthly") -> Decimal:
    price = get_plan_price(plan_id, billing_cycle)
    return price / 12 if billing_cycle == "annual" else price


def identify_subscription_by_value(value: Decimal) -> tuple[str, str] | None:
    normalized = value.quantize(Decimal("0.01"))
    return next(
        (
            (plan_id, billing_cycle)
            for plan_id, config in PLAN_CONFIG.items()
            if plan_id != "free"
            for billing_cycle, price in config["prices"].items()
            if price == normalized
        ),
        None,
    )


def identify_plan_by_value(value: Decimal) -> str | None:
    match = identify_subscription_by_value(value)
    return match[0] if match else None
