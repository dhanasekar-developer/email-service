from app.db.base import Base
from app.core.config import settings
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Enum as SqlEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from enum import Enum
import uuid


class StatusType(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"

class TemplateName(str, Enum):
    PORTFOLIO = 'portfolio'
    WELCOME = 'welcome'
    OTP = 'otp'


class EmailRecord(Base):

    __tablename__ = 'email_record'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    subject: Mapped[str] = mapped_column(String(255))

    message: Mapped[str | None] = mapped_column(String, nullable=True)

    to_email: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    cc_email: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    context: Mapped[dict] = mapped_column(JSONB)

    template_name: Mapped[TemplateName] = mapped_column(SqlEnum(TemplateName, name='template_name', schema=settings.SCHEMA), nullable=False)

    attachments: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    status: Mapped[StatusType] = mapped_column(SqlEnum(StatusType, name="status_type", schema=settings.SCHEMA), nullable=False, default=StatusType.PENDING, index=True)

    provider_message_id: Mapped[str | None] = mapped_column(String, nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    last_error: Mapped[str | None] = mapped_column(String, nullable=True)

    next_retry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)