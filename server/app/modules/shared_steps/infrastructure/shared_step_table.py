from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class SharedStepTable(TableBase):
    __tablename__ = "shared_steps"
    __table_args__ = (UniqueConstraint("project_id", "key"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    key: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    current_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("shared_step_versions.id", name="shared_steps_current_version_id_fkey", use_alter=True)
    )
    archived_at: Mapped[datetime | None]
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
