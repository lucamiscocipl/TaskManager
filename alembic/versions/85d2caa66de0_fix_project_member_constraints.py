"""fix project member constraints

Revision ID: 85d2caa66de0
Revises: c282cbccce40
Create Date: 2026-07-20 15:28:10.320242

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "85d2caa66de0"
down_revision: Union[str, Sequence[str], None] = "c282cbccce40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "project_members",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "project_members_user_id_fkey",
        "project_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "project_members_pkey",
        "project_members",
        type_="primary",
    )

    op.create_primary_key(
        "project_members_pkey",
        "project_members",
        ["project_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "project_members_pkey",
        "project_members",
        type_="primary",
    )

    op.create_primary_key(
        "project_members_pkey",
        "project_members",
        ["project_id"],
    )

    op.drop_constraint(
        "project_members_user_id_fkey",
        "project_members",
        type_="foreignkey",
    )

    op.alter_column(
        "project_members",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
