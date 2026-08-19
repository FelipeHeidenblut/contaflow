import uuid

from database import Base
from enums import TaskStatus  # Importando o Enum
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
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
    billing_cycle = Column(String(20), default="monthly", nullable=False)
    status_pagamento = Column(String, default="ativo")
    calendar_token = Column(String(64), unique=True, nullable=True, index=True)


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint(
            "alert_advance_hours IN (48, 72, 168)",
            name="ck_profiles_alert_advance_hours",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(String, unique=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Text, default="colaborador")
    is_superadmin = Column(Boolean, default=False, nullable=False)
    deadline_alerts_enabled = Column(Boolean, default=False, nullable=False)
    alert_advance_hours = Column(Integer, default=72, nullable=False)
    calendar_token = Column(String(64), unique=True, nullable=True, index=True)

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
    email = Column(String(320), nullable=True)
    responsible_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


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
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(String(20), default="success", nullable=False, index=True)
    error = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DeadlineAlert(Base):
    __tablename__ = "deadline_alerts"
    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "due_date",
            "lead_hours",
            "recipient_profile_id",
            name="uq_deadline_alert_task_due_lead_profile",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    due_date = Column(Date, nullable=False)
    lead_hours = Column(Integer, nullable=False)
    recipient_email = Column(String(320), nullable=False)
    status = Column(String(20), default="processing", nullable=False)
    attempts = Column(Integer, default=1, nullable=False)
    last_error = Column(String(1000), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content = Column(String(2000), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_payment_id = Column(String(100), unique=True, nullable=False)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subscription_id = Column(String(100), nullable=True)
    value = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    due_date = Column(Date, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True, index=True)
    invoice_url = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(80), nullable=False)
    reason = Column(String(500), nullable=False)
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
