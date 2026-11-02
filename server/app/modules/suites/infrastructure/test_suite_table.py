from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.suites.typing.constants.suite import ACTIVE_SUITE_NAME_INDEX
from app.shared.postgres import TableBase


class TestSuiteTable(TableBase):
    __tablename__ = "test_suites"
    __table_args__ = (
        Index(
            ACTIVE_SUITE_NAME_INDEX,
            "project_id",
            func.lower(text("name")),
            unique=True,
            postgresql_where=text("archived_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    archived_at: Mapped[datetime | None]
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
