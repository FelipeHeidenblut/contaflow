from datetime import datetime
from typing import Optional
from uuid import UUID

import models
from access_control import get_accessible_client, has_management_access
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from security import get_active_user, get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/comentarios", tags=["Comentários internos"])


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: UUID
    task_id: Optional[UUID] = None
    content: str = Field(..., min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O comentário não pode ficar vazio.")
        return normalized


class CommentResponse(BaseModel):
    id: UUID
    client_id: UUID
    task_id: Optional[UUID]
    author_id: Optional[UUID]
    author_name: str
    content: str
    created_at: datetime


def _serialize_comment(comment: models.Comment, author_name: str) -> dict:
    return {
        "id": comment.id,
        "client_id": comment.client_id,
        "task_id": comment.task_id,
        "author_id": comment.author_id,
        "author_name": author_name or "Usuário removido",
        "content": comment.content,
        "created_at": comment.created_at,
    }


@router.get("", response_model=list[CommentResponse])
def list_comments(
    client_id: UUID = Query(...),
    task_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    get_accessible_client(db, client_id, current_user)
    query = (
        db.query(models.Comment, models.Profile.name)
        .outerjoin(models.Profile, models.Comment.author_id == models.Profile.id)
        .filter(
            models.Comment.tenant_id == current_user["tenant_id"],
            models.Comment.client_id == client_id,
        )
    )
    if task_id:
        task = (
            db.query(models.Task)
            .filter(
                models.Task.id == task_id,
                models.Task.tenant_id == current_user["tenant_id"],
                models.Task.client_id == client_id,
            )
            .first()
        )
        if not task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada para este cliente.")
        query = query.filter(models.Comment.task_id == task_id)
    else:
        query = query.filter(models.Comment.task_id.is_(None))
    return [
        _serialize_comment(comment, author_name)
        for comment, author_name in query.order_by(models.Comment.created_at.asc()).all()
    ]


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    get_accessible_client(db, payload.client_id, current_user, active_only=True)
    if payload.task_id:
        task = (
            db.query(models.Task)
            .filter(
                models.Task.id == payload.task_id,
                models.Task.tenant_id == current_user["tenant_id"],
                models.Task.client_id == payload.client_id,
            )
            .first()
        )
        if not task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada para este cliente.")

    comment = models.Comment(
        tenant_id=current_user["tenant_id"],
        client_id=payload.client_id,
        task_id=payload.task_id,
        author_id=current_user["user_id"],
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    author = db.query(models.Profile).filter(models.Profile.id == current_user["user_id"]).first()
    return _serialize_comment(comment, author.name if author else "Usuário")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_active_user),
):
    comment = (
        db.query(models.Comment)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.tenant_id == current_user["tenant_id"],
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    get_accessible_client(db, comment.client_id, current_user)
    if str(comment.author_id) != str(current_user["user_id"]) and not has_management_access(
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode remover seus próprios comentários.",
        )
    db.delete(comment)
    db.commit()
    return None
