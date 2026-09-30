"""add student_id FK to absence and replacement tb

Revision ID: 5d09dda01227
Revises: eee9c2756a60
Create Date: 2026-09-30 18:55:45.723745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d09dda01227'
down_revision: Union[str, Sequence[str], None] = 'eee9c2756a60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass