from decimal import Decimal
from typing import Literal

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
PlanLimitResource = Literal["clients", "members"]


def get_plan_config(plan_id: str) -> dict:
    return PLAN_CONFIG.get(plan_id, PLAN_CONFIG["free"])


def get_plan_name(plan_id: str) -> str:
    return get_plan_config(plan_id)["name"]


def get_plan_limit(
    plan_id: str,
    resource: PlanLimitResource,
) -> int | None:
    return get_plan_config(plan_id)[resource]


def get_plan_price(plan_id: str, billing_cycle: str = "monthly") -> Decimal:
    plan = get_plan_config(plan_id)
    cycle = billing_cycle if billing_cycle in BILLING_CYCLES else "monthly"
    return plan["prices"][cycle]


def get_monthly_equivalent(plan_id: str, billing_cycle: str = "monthly") -> Decimal:
    price = get_plan_price(plan_id, billing_cycle)
    return price / 12 if billing_cycle == "annual" else price
