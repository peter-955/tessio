from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class RunFileTable(TableBase):
    __tablename__ = "run_files"
    __table_args__ = (UniqueConstraint("run_id", "test_case_id", "key"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("runs.id"))
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    test_file_version_id: Mapped[UUID] = mapped_column(ForeignKey("test_file_versions.id"))
    key: Mapped[str]
    requested_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
