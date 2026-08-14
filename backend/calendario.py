import secrets
from datetime import datetime, timezone

import models
from access_control import apply_task_scope
from database import get_db
from enums import TaskStatus
from fastapi import APIRouter, Depends, HTTPException, Response, status
from icalendar import Calendar, Event
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/calendario", tags=["Calendário e Sincronização"])


def ensure_calendar_token(profile: models.Profile, db: Session) -> str:
    if not profile.calendar_token:
        profile.calendar_token = secrets.token_urlsafe(32)
        db.commit()
        db.refresh(profile)
    return profile.calendar_token


@router.get("/feed-url")
def obter_feed_url(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    profile = db.query(models.Profile).filter(
        models.Profile.id == current_user["user_id"],
        models.Profile.tenant_id == current_user["tenant_id"],
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return {"token": ensure_calendar_token(profile, db)}


@router.post("/feed-token/rotate")
def rotacionar_feed_token(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    profile = db.query(models.Profile).filter(
        models.Profile.id == current_user["user_id"],
        models.Profile.tenant_id == current_user["tenant_id"],
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    profile.calendar_token = secrets.token_urlsafe(32)
    db.commit()
    return {"token": profile.calendar_token}


@router.get("/feed/{calendar_token}.ics")
def gerar_ics_feed(calendar_token: str, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(
        models.Profile.calendar_token == calendar_token
    ).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed não encontrado.")

    cal = Calendar()
    cal.add("prodid", "-//ContablyTask//Contabil//BR")
    cal.add("version", "2.0")
    task_query = db.query(models.Task).filter(
        models.Task.tenant_id == profile.tenant_id,
        models.Task.status != TaskStatus.CONCLUIDA.value,
    )
    tarefas = apply_task_scope(
        task_query,
        {
            "user_id": str(profile.id),
            "tenant_id": str(profile.tenant_id),
            "role": profile.role,
        },
    ).all()

    for tarefa in tarefas:
        event = Event()
        event.add("summary", f"📋 {tarefa.title}")
        event.add("description", tarefa.description or "Tarefa do ContablyTask")
        event.add("dtstart", tarefa.due_date)
        event.add("dtend", tarefa.due_date)
        event.add("dtstamp", datetime.now(timezone.utc))
        event["uid"] = f"task-{tarefa.id}@contablytask.com.br"
        cal.add_component(event)

    for prazo in db.query(models.TaxDeadline).all():
        event = Event()
        event.add("summary", f"🏛️ {prazo.title}")
        event.add("description", prazo.description or "Prazo Federal")
        event.add("dtstart", prazo.deadline_date)
        event.add("dtend", prazo.deadline_date)
        event.add("dtstamp", datetime.now(timezone.utc))
        event["uid"] = f"federal-{prazo.id}@contablytask.com.br"
        cal.add_component(event)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Cache-Control": "private, max-age=300", "X-Robots-Tag": "noindex, nofollow"},
    )
