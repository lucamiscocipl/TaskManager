"""your change

Revision ID: c282cbccce40
Revises: 0d21a5e45f04
Create Date: 2026-07-20 13:28:11.661492

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c282cbccce40"
down_revision: Union[str, Sequence[str], None] = "0d21a5e45f04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration is intentionally a no-op because the initial schema was
    # already created in the database and the app now relies on Alembic for
    # future changes.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
