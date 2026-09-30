"""add student_id FK to absence and replacement tb

Revision ID: eee9c2756a60
Revises: 55f8dde561b3
Create Date: 2026-09-30 18:48:11.457107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eee9c2756a60'
down_revision: Union[str, Sequence[str], None] = '55f8dde561b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass