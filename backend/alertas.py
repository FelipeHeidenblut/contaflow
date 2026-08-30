"""HTTP contract for deadline alerts."""

from typing import Literal

from alert_service import (
    get_alert_preferences as get_preferences,
    is_due_for_alert,
    lead_time_label,
    process_due_alerts,
    update_alert_preferences as update_preferences,
    verify_cron_secret,
)
from database import get_db
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict
from security import get_active_user
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1/alertas", tags=["Alertas de vencimento"])


class AlertPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deadline_alerts_enabled: bool = False
    alert_advance_hours: Literal[48, 72, 168] = 72


@router.get("/preferencias")
def get_alert_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return get_preferences(db, current_user)


@router.put("/preferencias")
def update_alert_preferences(
    preferences: AlertPreferences,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    return update_preferences(
        db,
        current_user,
        enabled=preferences.deadline_alerts_enabled,
        advance_hours=preferences.alert_advance_hours,
    )


@router.post("/processar")
def process_alerts_endpoint(
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
    db: Session = Depends(get_db),
):
    verify_cron_secret(x_cron_secret)
    result = process_due_alerts(db)
    if result["failed"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{result['failed']} alerta(s) não puderam ser enviados.",
        )
    return result
