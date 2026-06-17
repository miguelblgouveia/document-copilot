from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base, TimestampMixin


class SourceDocument(TimestampMixin, Base):
    __tablename__ = "source_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticker: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    filing_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    filing_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    accession_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    filing_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    chunks = relationship("DocumentChunk", back_populates="source_document")
