import pytest

import plan_config


@pytest.mark.parametrize(
    ("plan_id", "resource", "expected"),
    [
        ("free", "clients", 5),
        ("profissional", "members", 10),
        ("business", "clients", None),
        ("unknown", "members", 1),
    ],
)
def test_get_plan_limit_uses_catalog_and_safe_free_fallback(
    plan_id,
    resource,
    expected,
):
    assert plan_config.get_plan_limit(plan_id, resource) == expected


def test_get_plan_name_uses_safe_free_fallback():
    assert plan_config.get_plan_name("escritorio") == "Escritório"
    assert plan_config.get_plan_name("unknown") == "Gratuito"
