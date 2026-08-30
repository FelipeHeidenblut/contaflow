"""HTTP contract for operational reports."""

from datetime import date
from uuid import UUID

from database import get_db
from fastapi import APIRouter, Depends, Query
from report_service import (
    build_report,
    ensure_report_access,
    generate_report,
    get_report_capabilities,
)
from security import get_current_user
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/v1/relatorios", tags=["Relatórios"])


def require_paid_reports(current_user: dict = Depends(get_current_user)):
    return ensure_report_access(current_user)


@router.get("")
def get_reports(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: UUID | None = Query(None),
    member_id: UUID | None = Query(None),
    task_status: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_paid_reports),
):
    return generate_report(
        db,
        current_user,
        start_date=start_date,
        end_date=end_date,
        client_id=client_id,
        member_id=member_id,
        task_status=task_status,
    )
