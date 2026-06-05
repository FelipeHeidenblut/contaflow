from datetime import date, datetime
from typing import Optional
from uuid import UUID

from enums import TaskStatus  # Importando o Enum
from pydantic import BaseModel, ConfigDict, Field


# ================== CLIENTES ==================
class ClientBase(BaseModel):
    razao_social: str
    # Validação básica de formato de CNPJ (XX.XXX.XXX/0001-XX)
    cnpj: str = Field(..., pattern=r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$")
    regime_tributario: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    ativo: bool


# ================== TAREFAS ==================
class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    description: Optional[str] = None
    due_date: date
    status: TaskStatus = TaskStatus.PENDENTE  # Usando Enum
    client_id: UUID
    assigned_to: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime


# ================== DOCUMENTOS ==================
class DocumentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: UUID
    task_id: Optional[UUID] = None
    nome_arquivo: str
    storage_path: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: UUID
    tenant_id: UUID
    uploaded_by: Optional[UUID] = None
    created_at: datetime


# ================== DASHBOARD ==================
class DashboardResponse(BaseModel):
    total_clientes: int
    tarefas_abertas: int
    tarefas_atrasadas: int
    model_config = ConfigDict(from_attributes=True)
