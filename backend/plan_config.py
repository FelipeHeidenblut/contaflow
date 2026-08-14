from decimal import Decimal

PLAN_CONFIG = {
    "free": {
        "name": "Gratuito",
        "price": Decimal("0.00"),
        "clients": 5,
        "members": 1,
    },
    "basico": {
        "name": "Essencial",
        "price": Decimal("79.90"),
        "clients": 40,
        "members": 5,
    },
    "profissional": {
        "name": "Profissional",
        "price": Decimal("149.90"),
        "clients": 100,
        "members": 10,
    },
    "business": {
        "name": "Empresarial",
        "price": Decimal("449.00"),
        "clients": None,
        "members": None,
    },
}

PAID_PLAN_IDS = {"basico", "profissional", "business"}


def get_plan_price(plan_id: str) -> Decimal:
    return PLAN_CONFIG.get(plan_id, PLAN_CONFIG["free"])["price"]


def identify_plan_by_value(value: Decimal) -> str | None:
    normalized = value.quantize(Decimal("0.01"))
    return next(
        (
            plan_id
            for plan_id, config in PLAN_CONFIG.items()
            if plan_id != "free" and config["price"] == normalized
        ),
        None,
    )

