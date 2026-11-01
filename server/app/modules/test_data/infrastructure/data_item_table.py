from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, LargeBinary, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.test_data.typing.enums import DataItemKind
from app.shared.postgres import TableBase, build_text_enum


class DataItemTable(TableBase):
    __tablename__ = "test_data"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "environment_id", "key", name="uq_test_data_scope_key", postgresql_nulls_not_distinct=True
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    environment_id: Mapped[UUID | None] = mapped_column(ForeignKey("environments.id", ondelete="CASCADE"), index=True)
    key: Mapped[str]
    kind: Mapped[DataItemKind] = mapped_column(build_text_enum(DataItemKind, "data_item_kind"))
    value: Mapped[str | None] = mapped_column(Text)
    value_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    created_at: Mapped[datetime]
