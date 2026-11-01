from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.stories.typing.enums import SprintState
from app.shared.postgres import TableBase, build_text_enum


class SprintTable(TableBase):
    __tablename__ = "sprints"
    __table_args__ = (UniqueConstraint("project_id", "jira_sprint_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    jira_sprint_id: Mapped[int]
    name: Mapped[str]
    state: Mapped[SprintState] = mapped_column(build_text_enum(SprintState, "sprint_state"))
    start_at: Mapped[datetime | None]
    end_at: Mapped[datetime | None]
    complete_at: Mapped[datetime | None]
    synced_at: Mapped[datetime]
    created_at: Mapped[datetime]
