from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from app.database.models.base import Base, TimestampMixin


class ChatMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(TimestampMixin, Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ChatMessageRole] = mapped_column(
        Enum(
            ChatMessageRole,
            name="chat_message_role",
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )
    message_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    thread = relationship("ChatThread", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
    citations = relationship("MessageCitation", back_populates="message")
