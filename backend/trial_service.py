"""Trial entitlements are evaluated on every request, independently of billing jobs."""
from datetime import datetime, timedelta, timezone
from math import ceil

from plan_config import PAID_PLAN_IDS

TRIAL_DAYS = 14


def trial_details(tenant, now=None):
    now = now or datetime.now(timezone.utc)
    start = getattr(tenant, "trial_started_at", None)
    end = getattr(tenant, "trial_ends_at", None)
    converted = getattr(tenant, "trial_converted_at", None)
    paid = tenant.plano in PAID_PLAN_IDS
    state = "none"
    if start and end:
        if converted or paid:
            state = "converted"
        elif start <= now < end:
            state = "active"
        else:
            state = "expired"
    return {
        "status": state,
        "started_at": start,
        "ends_at": end,
        "days_remaining": max(0, ceil((end - now).total_seconds() / 86400)) if state == "active" else 0,
    }


def effective_plan(tenant, now=None):
    return "profissional" if trial_details(tenant, now)["status"] == "active" else tenant.plano


def start_trial(tenant, now=None):
    if getattr(tenant, "trial_started_at", None) or tenant.plano in PAID_PLAN_IDS:
        return
    now = now or datetime.now(timezone.utc)
    tenant.trial_started_at = now
    tenant.trial_ends_at = now + timedelta(days=TRIAL_DAYS)
