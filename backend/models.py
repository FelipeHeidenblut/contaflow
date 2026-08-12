import uuid

from database import Base
from enums import TaskStatus  # Importando o Enum
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    razao_social = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    asaas_customer_id = Column(String, nullable=True)
    asaas_subscription_id = Column(String, nullable=True, unique=True)
    plano = Column(String, default="free")
    status_pagamento = Column(String, default="ativo")
    calendar_token = Column(String(64), unique=True, nullable=True, index=True)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(String, unique=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Text, default="user")
    is_superadmin = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("tenant_id", "cnpj", name="uq_clients_tenant_cnpj"),
        UniqueConstraint("tenant_id", "cpf", name="uq_clients_tenant_cpf"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Novos campos
    tipo_pessoa = Column(String, default="PJ")  # PJ ou PF
    nome = Column(String, nullable=True)  # Para PF
    cpf = Column(String, nullable=True)  # Para PF

    # Antigos campos (Agora opcionais)
    razao_social = Column(String, nullable=True)  # Mudança crítica aqui
    cnpj = Column(String, nullable=True)  # Mudança crítica aqui

    regime_tributario = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

    natureza_operacao = Column(
        String, default="Serviços"
    )  # Comércio, Serviços, Indústria


class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    assigned_to = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL")
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        String(50), default=TaskStatus.PENDENTE.value, nullable=False
    )  # Usando o Enum
    due_date = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_recurring = Column(Boolean, default=False)

    recurrence_day = Column(Integer, nullable=True)
    # Dentro da classe Tarefa
    grau_importancia = Column(String, default="Média")


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"))
    nome_arquivo = Column(String(255), nullable=False)
    categoria = Column(String(40), nullable=False, default="Geral", server_default="Geral")
    storage_path = Column(String(500), nullable=False)
    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL")
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TaxDeadline(Base):
    __tablename__ = "tax_deadlines"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    deadline_date = Column(Date, nullable=False)
    is_monthly = Column(Boolean, default=False)
    reference_link = Column(String, nullable=True)


class AsaasWebhookEvent(Base):
    __tablename__ = "asaas_webhook_events"

    id = Column(String(100), primary_key=True)
    event_type = Column(String(80), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
