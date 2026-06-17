from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database.models.base import Base, TimestampMixin


class DocumentChunk(TimestampMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("source_document_id", "chunk_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.genai_embedding_dimensions),
        nullable=False,
    )
    # The generated expression should be added explicitly in Alembic migration.
    search_vector: Mapped[str] = mapped_column(TSVECTOR, nullable=False)

    source_document = relationship("SourceDocument", back_populates="chunks")
    citations = relationship("MessageCitation", back_populates="chunk")
