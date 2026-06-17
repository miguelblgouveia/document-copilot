from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base, TimestampMixin


class MessageCitation(TimestampMixin, Base):
    __tablename__ = "message_citations"
    __table_args__ = (UniqueConstraint("message_id", "citation_index"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    citation_index: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    quote_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int | None] = mapped_column(Integer, nullable=True)

    message = relationship("ChatMessage", back_populates="citations")
    chunk = relationship("DocumentChunk", back_populates="citations")
