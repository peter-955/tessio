from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.postgres import TableBase, build_text_enum


class ProjectSyncStateTable(TableBase):
    __tablename__ = "project_sync_states"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    status: Mapped[ProjectSyncStatus] = mapped_column(build_text_enum(ProjectSyncStatus, "project_sync_status"))
    requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    queued_at: Mapped[datetime | None]
    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]
    last_succeeded_at: Mapped[datetime | None]
    error_code: Mapped[str | None]
    created_at: Mapped[datetime]
