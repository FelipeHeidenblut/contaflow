import uuid

from database import Base
from enums import TaskStatus  # Importando o Enum
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
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


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(String, unique=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Text)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    razao_social = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=False)
    regime_tributario = Column(String(50))
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Garante que um mesmo escritório não cadastre o mesmo CNPJ duas vezes
    __table_args__ = (UniqueConstraint("tenant_id", "cnpj", name="uq_tenant_cnpj"),)


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
    storage_path = Column(String(500), nullable=False)
    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL")
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
