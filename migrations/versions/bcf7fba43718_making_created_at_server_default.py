"""making created_at server default

Revision ID: bcf7fba43718
Revises: 93584b655c7d
Create Date: 2025-11-20 16:05:51.299328

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bcf7fba43718"
down_revision: Union[str, Sequence[str], None] = "93584b655c7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "user",
        "created_at",
        nullable=False,
        server_default=sa.text("current_timestamp"),
    )
    op.alter_column(
        "author",
        "created_at",
        nullable=False,
        server_default=sa.text("current_timestamp"),
    )
    op.alter_column(
        "book",
        "created_at",
        nullable=False,
        server_default=sa.text("current_timestamp"),
    )
    op.alter_column(
        "book_authorship",
        "created_at",
        nullable=False,
        server_default=sa.text("current_timestamp"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("user", "created_at", nullable=False)
    op.alter_column("author", "created_at", nullable=False)
    op.alter_column("book", "created_at", nullable=False)
    op.alter_column(
        "book_authorship",
        "created_at",
        nullable=False,
    )
