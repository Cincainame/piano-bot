"""add student term absence and replacement tables

Revision ID: 8f4c2d7a1b90
Revises: 123c59c55269
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8f4c2d7a1b90"
down_revision: Union[str, Sequence[str], None] = "123c59c55269"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if sa.inspect(bind).has_table("student"):
        op.add_column(
            "student",
            sa.Column("phone_no", sa.String(length=32), nullable=False, server_default=""),
        )
        op.alter_column("student", "phone_no", server_default=None)
    else:
        op.create_table(
            "student",
            sa.Column("id", sa.BigInteger(), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("start_time", sa.Time(), nullable=False),
            sa.Column("end_time", sa.Time(), nullable=False),
            sa.Column("phone_no", sa.String(length=32), nullable=False),
        )
    op.create_table(
        "term",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "student_id",
            sa.BigInteger(),
            sa.ForeignKey("student.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("term", postgresql.ARRAY(sa.Integer()), nullable=False),
    )
    op.create_table(
        "replacement",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "term_id",
            sa.BigInteger(),
            sa.ForeignKey("term.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("replacement_date", sa.Date(), nullable=False),
    )
    op.create_table(
        "absence",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "term_id",
            sa.BigInteger(),
            sa.ForeignKey("term.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("absent_date", sa.Date(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("absence")
    op.drop_table("replacement")
    op.drop_table("term")
    op.drop_table("student")