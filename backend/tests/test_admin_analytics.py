from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from admin import (
    AdminStatusUpdate,
    _latest_activity,
    _mask_provider_id,
    _percentage_change,
    _shift_month,
)
from plan_config import (
    get_monthly_equivalent,
    get_plan_price,
    identify_plan_by_value,
    identify_subscription_by_value,
)


def test_shift_month_handles_year_boundaries():
    assert _shift_month(date(2026, 1, 1), -1) == date(2025, 12, 1)
    assert _shift_month(date(2026, 12, 1), 1) == date(2027, 1, 1)


def test_percentage_change_handles_missing_comparison_base():
    assert _percentage_change(0, 0) is None
    assert _percentage_change(10, 0) == 100.0
    assert _percentage_change(75, 100) == -25.0


def test_latest_activity_ignores_empty_sources():
    earlier = datetime(2026, 8, 1, tzinfo=timezone.utc)
    later = datetime(2026, 8, 10, tzinfo=timezone.utc)

    assert _latest_activity(None, earlier, later) == later
    assert _latest_activity(None, None) is None


def test_provider_identifier_is_masked():
    assert _mask_provider_id("cus_123456789") == "••••456789"
    assert _mask_provider_id(None) is None


def test_plan_is_identified_from_exact_payment_value():
    assert identify_plan_by_value(Decimal("149.90")) == "profissional"
    assert identify_plan_by_value(Decimal("149.9")) == "profissional"
    assert identify_subscription_by_value(Decimal("2499")) == ("escritorio", "annual")
    assert get_plan_price("escritorio", "monthly") == Decimal("249.90")
    assert get_plan_price("escritorio", "annual") == Decimal("2499.00")
    assert get_monthly_equivalent("business", "annual").quantize(Decimal("0.01")) == Decimal(
        "374.17"
    )
    assert identify_plan_by_value(Decimal("150.00")) is None
    assert get_plan_price("unknown") == Decimal("0.00")


def test_manual_status_change_requires_a_meaningful_reason():
    payload = AdminStatusUpdate(status="inadimplente", reason="Solicitado pelo financeiro")
    assert payload.status == "inadimplente"

    with pytest.raises(ValidationError):
        AdminStatusUpdate(status="ativo", reason="x")

    with pytest.raises(ValidationError):
        AdminStatusUpdate(status="cancelado", reason="Solicitado pelo financeiro")
