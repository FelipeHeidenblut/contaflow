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
    Integer
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
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Novos campos
    tipo_pessoa = Column(String, default="PJ")  # PJ ou PF
    nome = Column(String, nullable=True)  # Para PF
    cpf = Column(String, nullable=True)  # Para PF

    # Antigos campos (Agora opcionais)
    razao_social = Column(String, nullable=True)  # Mudança crítica aqui
    cnpj = Column(String, nullable=True)  # Mudança crítica aqui

    regime_tributario = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)


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
    
class TaxDeadline(Base):
    __tablename__ = "tax_deadlines"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    deadline_date = Column(Date, nullable=False)
    is_monthly = Column(Boolean, default=False)
    reference_link = Column(String, nullable=True)
