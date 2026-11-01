from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "language",
            sa.Enum("en", "fr", "vi", name="user_language", native_enum=False, create_constraint=True, length=40),
            server_default="en",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "color_scheme",
            sa.Enum("light", "dark", "auto", name="color_scheme", native_enum=False, create_constraint=True, length=40),
            server_default="auto",
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("avatar_file_id", sa.Uuid(), nullable=True))
    op.add_column("users", sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("users_avatar_file_id_fkey", "users", "stored_files", ["avatar_file_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("users_avatar_file_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "deactivated_at")
    op.drop_column("users", "avatar_file_id")
    op.drop_column("users", "color_scheme")
    op.drop_column("users", "language")
