from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestFileVersionTable(TableBase):
    __tablename__ = "test_file_versions"
    __table_args__ = (UniqueConstraint("test_file_id", "number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    test_file_id: Mapped[UUID] = mapped_column(ForeignKey("test_files.id"))
    number: Mapped[int]
    stored_file_id: Mapped[UUID] = mapped_column(ForeignKey("stored_files.id"), unique=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
