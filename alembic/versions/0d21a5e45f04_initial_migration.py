"""initial migration

Revision ID: 0d21a5e45f04
Revises:
Create Date: 2026-07-20 13:20:20.160194

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d21a5e45f04"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    return bind.dialect.has_table(bind, table_name)


def upgrade() -> None:
    """Create the initial schema."""
    bind = op.get_bind()

    if not _table_exists(bind, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("username", sa.String(length=25), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("users_pkey")),
            sa.UniqueConstraint(
                "username",
                name=op.f("users_username_key"),
                postgresql_include=[],
                postgresql_nulls_not_distinct=False,
            ),
        )

    if not _table_exists(bind, "projects"):
        op.create_table(
            "projects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["owner_id"], ["users.id"], name=op.f("projects_owner_id_fkey")
            ),
            sa.PrimaryKeyConstraint("id", name=op.f("projects_pkey")),
        )

    if not _table_exists(bind, "tasks"):
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["project_id"], ["projects.id"], name=op.f("tasks_project_id_fkey")
            ),
            sa.ForeignKeyConstraint(
                ["user_id"], ["users.id"], name=op.f("tasks_user_id_fkey")
            ),
            sa.PrimaryKeyConstraint("id", name=op.f("tasks_pkey")),
        )

    if not _table_exists(bind, "project_members"):
        op.create_table(
            "project_members",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column(
                "joined_at",
                postgresql.TIMESTAMP(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["project_id"],
                ["projects.id"],
                name=op.f("project_members_project_id_fkey"),
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name=op.f("project_members_user_id_fkey"),
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "project_id", "user_id", name=op.f("project_members_pkey")
            ),
        )


def downgrade() -> None:
    """Drop the initial schema."""
    for table_name in ["project_members", "tasks", "projects", "users"]:
        op.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
