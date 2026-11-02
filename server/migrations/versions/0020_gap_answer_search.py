from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEARCH_VECTOR_EXPRESSION = "to_tsvector('simple'::regconfig, question || ' ' || coalesce(answer, ''))"


def upgrade() -> None:
    op.add_column("gaps", sa.Column("answered_via_token_id", sa.Uuid(), nullable=True))
    op.add_column(
        "gaps",
        sa.Column("search_vector", TSVECTOR(), sa.Computed(SEARCH_VECTOR_EXPRESSION, persisted=True), nullable=True),
    )
    op.create_index("ix_gaps_search_vector", "gaps", ["search_vector"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("ix_gaps_search_vector", table_name="gaps", postgresql_using="gin")
    op.drop_column("gaps", "search_vector")
    op.drop_column("gaps", "answered_via_token_id")
