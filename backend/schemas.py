import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from enums import TaskStatus  # Importando o Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator


# ================== CLIENTES ==================
class ClientBase(BaseModel):
    tipo_pessoa: str = "PJ"  # Valor padrão para manter compatibilidade
    razao_social: Optional[str] = None  # Agora opcional
    cnpj: Optional[str] = None  # Agora opcional
    nome: Optional[str] = None  # Novo campo PF
    cpf: Optional[str] = None  # Novo campo PF
    regime_tributario: str = Field(..., min_length=2, max_length=80)
    natureza_operacao: str = Field(default="Serviços", min_length=2, max_length=80)


class ClientCreate(ClientBase):
    @model_validator(mode="after")
    def check_pessoa_fields(self):
        if self.tipo_pessoa == "PJ":
            if not self.razao_social:
                raise ValueError("Razão Social é obrigatória para Pessoa Jurídica")
            normalized = re.sub(r"[^A-Za-z0-9]", "", self.cnpj or "").upper()
            if len(normalized) != 14:
                raise ValueError("CNPJ deve conter 14 caracteres.")
            self.cnpj = normalized
        elif self.tipo_pessoa == "PF":
            if not self.nome:
                raise ValueError("Nome completo é obrigatório para Pessoa Física")
            normalized = re.sub(r"\D", "", self.cpf or "")
            if len(normalized) != 11:
                raise ValueError("CPF deve conter 11 dígitos.")
            self.cpf = normalized
        else:
            raise ValueError('tipo_pessoa deve ser "PF" ou "PJ"')

        return self


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    ativo: bool


# ================== TAREFAS ==================
class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4000)
    due_date: date
    status: TaskStatus = TaskStatus.PENDENTE  # Usando Enum
    client_id: UUID
    assigned_to: Optional[UUID] = None
    grau_importancia: str = Field(default="Média", pattern="^(Baixa|Média|Alta|Urgente)$")
    is_recurring: bool = False
    recurrence_day: Optional[int] = Field(default=None, ge=1, le=31)

    @model_validator(mode="after")
    def check_recurrence(self):
        if self.is_recurring and self.recurrence_day is None:
            raise ValueError("recurrence_day é obrigatório para tarefas recorrentes")
        if not self.is_recurring:
            self.recurrence_day = None

        return self


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
    categoria: str = "Geral"
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
    plano: str
    status_pagamento: str
    model_config = ConfigDict(from_attributes=True)
