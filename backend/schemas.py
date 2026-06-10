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
    regime_tributario: Optional[str] = None


class ClientCreate(ClientBase):
    @model_validator(mode="after")
    def check_pessoa_fields(self):
        if self.tipo_pessoa == "PJ":
            if not self.razao_social:
                raise ValueError("Razão Social é obrigatória para Pessoa Jurídica")
            # Validação de formato de CNPJ
            if not self.cnpj or not re.match(
                r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$", self.cnpj
            ):
                raise ValueError(
                    "CNPJ inválido para Pessoa Jurídica (Formato: XX.XXX.XXX/0001-XX)"
                )
        elif self.tipo_pessoa == "PF":
            if not self.nome:
                raise ValueError("Nome completo é obrigatório para Pessoa Física")
            # Validação de formato de CPF
            if not self.cpf or not re.match(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", self.cpf):
                raise ValueError(
                    "CPF inválido para Pessoa Física (Formato: XXX.XXX.XXX-XX)"
                )
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
