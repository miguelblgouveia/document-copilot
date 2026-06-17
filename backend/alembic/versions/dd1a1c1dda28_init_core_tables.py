"""init core tables

Revision ID: dd1a1c1dda28
Revises: 
Create Date: 2026-06-17 09:46:09.547776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


EMBEDDING_DIMENSIONS = 768


# revision identifiers, used by Alembic.
revision: str = 'dd1a1c1dda28'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "source_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("filing_type", sa.String(length=64), nullable=False),
        sa.Column("filing_date", sa.Date(), nullable=False),
        sa.Column("accession_number", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("filing_year", sa.Integer(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_documents")),
        sa.UniqueConstraint(
            "accession_number",
            name=op.f("uq_source_documents_accession_number"),
        ),
    )
    op.create_index(op.f("ix_source_documents_ticker"), "source_documents", ["ticker"], unique=False)
    op.create_index(op.f("ix_source_documents_filing_type"), "source_documents", ["filing_type"], unique=False)
    op.create_index(op.f("ix_source_documents_filing_date"), "source_documents", ["filing_date"], unique=False)
    op.create_index(op.f("ix_source_documents_filing_year"), "source_documents", ["filing_year"], unique=False)

    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_name", sa.String(length=255), nullable=True),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "embedding",
            Vector(EMBEDDING_DIMENSIONS),
            nullable=False,
        ),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('english'::regconfig, coalesce(content_text, ''))",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_documents.id"],
            name=op.f("fk_document_chunks_source_document_id_source_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_chunks")),
        sa.UniqueConstraint(
            "source_document_id",
            "chunk_index",
            name=op.f("uq_document_chunks_source_document_id"),
        ),
    )
    op.create_index(op.f("ix_document_chunks_source_document_id"), "document_chunks", ["source_document_id"], unique=False)
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_search_vector_gin ON document_chunks USING gin (search_vector)"
    )

    op.create_table(
        "chat_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_chat_threads_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_threads")),
    )
    op.create_index(op.f("ix_chat_threads_user_id"), "chat_threads", ["user_id"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", name="chat_message_role", native_enum=False),
            nullable=False,
        ),
        sa.Column("message_index", sa.Integer(), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("message_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["chat_threads.id"],
            name=op.f("fk_chat_messages_thread_id_chat_threads"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_chat_messages_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_messages")),
        sa.UniqueConstraint("thread_id", "message_index", name=op.f("uq_chat_messages_thread_id")),
    )
    op.create_index(op.f("ix_chat_messages_thread_id"), "chat_messages", ["thread_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_user_id"), "chat_messages", ["user_id"], unique=False)

    op.create_table(
        "message_citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("citation_index", sa.Integer(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=True),
        sa.Column("quote_text", sa.Text(), nullable=True),
        sa.Column("start_char", sa.Integer(), nullable=True),
        sa.Column("end_char", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            name=op.f("fk_message_citations_chunk_id_document_chunks"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["chat_messages.id"],
            name=op.f("fk_message_citations_message_id_chat_messages"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_message_citations")),
        sa.UniqueConstraint("message_id", "citation_index", name=op.f("uq_message_citations_message_id")),
    )
    op.create_index(op.f("ix_message_citations_message_id"), "message_citations", ["message_id"], unique=False)
    op.create_index(op.f("ix_message_citations_chunk_id"), "message_citations", ["chunk_id"], unique=False)

    op.execute("ALTER TABLE chat_threads ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE message_citations ENABLE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY chat_threads_user_is_owner_select
        ON chat_threads
        FOR SELECT
        USING (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_threads_user_is_owner_insert
        ON chat_threads
        FOR INSERT
        WITH CHECK (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_threads_user_is_owner_update
        ON chat_threads
        FOR UPDATE
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_threads_user_is_owner_delete
        ON chat_threads
        FOR DELETE
        USING (user_id = auth.uid())
        """
    )

    op.execute(
        """
        CREATE POLICY chat_messages_user_is_owner_select
        ON chat_messages
        FOR SELECT
        USING (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_messages_user_is_owner_insert
        ON chat_messages
        FOR INSERT
        WITH CHECK (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_messages_user_is_owner_update
        ON chat_messages
        FOR UPDATE
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid())
        """
    )
    op.execute(
        """
        CREATE POLICY chat_messages_user_is_owner_delete
        ON chat_messages
        FOR DELETE
        USING (user_id = auth.uid())
        """
    )

    op.execute(
        """
        CREATE POLICY message_citations_user_is_owner_select
        ON message_citations
        FOR SELECT
        USING (
            EXISTS (
                SELECT 1
                FROM chat_messages cm
                WHERE cm.id = message_citations.message_id
                  AND cm.user_id = auth.uid()
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY message_citations_user_is_owner_insert
        ON message_citations
        FOR INSERT
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM chat_messages cm
                WHERE cm.id = message_citations.message_id
                  AND cm.user_id = auth.uid()
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY message_citations_user_is_owner_update
        ON message_citations
        FOR UPDATE
        USING (
            EXISTS (
                SELECT 1
                FROM chat_messages cm
                WHERE cm.id = message_citations.message_id
                  AND cm.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1
                FROM chat_messages cm
                WHERE cm.id = message_citations.message_id
                  AND cm.user_id = auth.uid()
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY message_citations_user_is_owner_delete
        ON message_citations
        FOR DELETE
        USING (
            EXISTS (
                SELECT 1
                FROM chat_messages cm
                WHERE cm.id = message_citations.message_id
                  AND cm.user_id = auth.uid()
            )
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP POLICY IF EXISTS message_citations_user_is_owner_delete ON message_citations")
    op.execute("DROP POLICY IF EXISTS message_citations_user_is_owner_update ON message_citations")
    op.execute("DROP POLICY IF EXISTS message_citations_user_is_owner_insert ON message_citations")
    op.execute("DROP POLICY IF EXISTS message_citations_user_is_owner_select ON message_citations")

    op.execute("DROP POLICY IF EXISTS chat_messages_user_is_owner_delete ON chat_messages")
    op.execute("DROP POLICY IF EXISTS chat_messages_user_is_owner_update ON chat_messages")
    op.execute("DROP POLICY IF EXISTS chat_messages_user_is_owner_insert ON chat_messages")
    op.execute("DROP POLICY IF EXISTS chat_messages_user_is_owner_select ON chat_messages")

    op.execute("DROP POLICY IF EXISTS chat_threads_user_is_owner_delete ON chat_threads")
    op.execute("DROP POLICY IF EXISTS chat_threads_user_is_owner_update ON chat_threads")
    op.execute("DROP POLICY IF EXISTS chat_threads_user_is_owner_insert ON chat_threads")
    op.execute("DROP POLICY IF EXISTS chat_threads_user_is_owner_select ON chat_threads")

    op.drop_index(op.f("ix_message_citations_chunk_id"), table_name="message_citations")
    op.drop_index(op.f("ix_message_citations_message_id"), table_name="message_citations")
    op.drop_table("message_citations")

    op.drop_index(op.f("ix_chat_messages_user_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_messages_thread_id"), table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index(op.f("ix_chat_threads_user_id"), table_name="chat_threads")
    op.drop_table("chat_threads")

    op.execute("DROP INDEX IF EXISTS ix_document_chunks_search_vector_gin")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
    op.drop_index(op.f("ix_document_chunks_source_document_id"), table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index(op.f("ix_source_documents_filing_year"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_filing_date"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_filing_type"), table_name="source_documents")
    op.drop_index(op.f("ix_source_documents_ticker"), table_name="source_documents")
    op.drop_table("source_documents")

    op.drop_table("users")
