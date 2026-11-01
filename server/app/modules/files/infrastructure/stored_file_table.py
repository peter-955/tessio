from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.shared.postgres import TableBase, build_text_enum


class StoredFileTable(TableBase):
    __tablename__ = "stored_files"
    __table_args__ = (Index("ix_stored_files_status_created_at", "status", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id"), index=True)
    kind: Mapped[StoredFileKind] = mapped_column(build_text_enum(StoredFileKind, "stored_file_kind"))
    object_key: Mapped[str] = mapped_column(Text, unique=True)
    file_name: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(Text)
    size: Mapped[int | None] = mapped_column(BigInteger)
    sha256: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StoredFileStatus] = mapped_column(build_text_enum(StoredFileStatus, "stored_file_status"))
    uploaded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime]
