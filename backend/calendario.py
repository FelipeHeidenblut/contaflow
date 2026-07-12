from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime
from icalendar import Calendar, Event
import models
from database import get_db
from enums import TaskStatus

router = APIRouter(prefix="/api/v1/calendario", tags=["Calendário e Sincronização"])

@router.get("/feed/{tenant_id}.ics")
def gerar_ics_feed(tenant_id: str, db: Session = Depends(get_db)):
    """
    Rota pública que gera um arquivo .ics dinâmico.
    O Google Agenda e o Outlook vão ler este link 1x por dia para atualizar as tarefas.
    """
    cal = Calendar()
    cal.add('prodid', '-//ContablyTask//Contabil//BR')
    cal.add('version', '2.0')

    # Busca todas as tarefas não concluídas daquele escritório
    tarefas = db.query(models.Task).filter(
        models.Task.tenant_id == tenant_id,
        models.Task.status != TaskStatus.CONCLUIDA.value
    ).all()

    # Busca os prazos federais globais
    prazos_federais = db.query(models.TaxDeadline).all()

    # Adiciona as tarefas internas ao calendário
    for t in tarefas:
        event = Event()
        event.add('summary', f"📋 {t.title}")
        event.add('description', t.description or "Tarefa do ContablyTask")
        event.add('dtstart', t.due_date)
        event.add('dtend', t.due_date)
        event.add('dtstamp', datetime.now())
        event['uid'] = f"task-{t.id}@contablytask.com.br" # ID único para o Google não duplicar
        cal.add_component(event)

    # Adiciona os prazos federais ao calendário
    for p in prazos_federais:
        event = Event()
        event.add('summary', f"🏛️ {p.title}")
        event.add('description', p.description or "Prazo Federal")
        event.add('dtstart', p.deadline_date)
        event.add('dtend', p.deadline_date)
        event.add('dtstamp', datetime.now())
        event['uid'] = f"federal-{p.id}@contaflow.com.br"
        cal.add_component(event)

    # Retorna o arquivo .ics puro
    return Response(content=cal.to_ical(), media_type="text/calendar")
