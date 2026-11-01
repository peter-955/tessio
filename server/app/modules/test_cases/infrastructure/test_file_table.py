from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestFileTable(TableBase):
    __tablename__ = "test_files"
    __table_args__ = (UniqueConstraint("test_case_id", "key"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    key: Mapped[str]
    current_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("test_file_versions.id", name="test_files_current_version_id_fkey", use_alter=True)
    )
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
