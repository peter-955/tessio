from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, Index, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.runs.typing.constants.run import RUNNING_RUN_PER_STORY_INDEX
from app.modules.runs.typing.enums import RunAbortReason, RunExecutor, RunStatus
from app.shared.postgres import TableBase, build_text_enum


class RunTable(TableBase):
    __tablename__ = "runs"
    __table_args__ = (
        Index(RUNNING_RUN_PER_STORY_INDEX, "story_id", unique=True, postgresql_where=text("status = 'running'")),
        Index("ix_runs_project_id_started_at", "project_id", "started_at"),
        Index("ix_runs_status_last_activity_at", "status", "last_activity_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"), index=True)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"), index=True)
    executor: Mapped[RunExecutor] = mapped_column(build_text_enum(RunExecutor, "run_executor"))
    status: Mapped[RunStatus] = mapped_column(build_text_enum(RunStatus, "run_status"))
    abort_reason: Mapped[RunAbortReason | None] = mapped_column(build_text_enum(RunAbortReason, "run_abort_reason"))
    parent_run_id: Mapped[UUID | None] = mapped_column(ForeignKey("runs.id"), index=True)
    started_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    started_via_token_id: Mapped[UUID | None] = mapped_column(Uuid)
    summary: Mapped[str | None] = mapped_column(Text)
    report: Mapped[JsonValue] = mapped_column(JSONB(none_as_null=True), nullable=True)
    started_at: Mapped[datetime]
    last_activity_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
