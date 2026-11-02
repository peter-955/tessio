from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.run_logs.typing.enums import RunLogEntryKind, RunLogPhase
from app.shared.postgres import TableBase, build_text_enum


class RunLogEntryTable(TableBase):
    __tablename__ = "run_log_entries"
    __table_args__ = (UniqueConstraint("run_id", "position"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("runs.id"), index=True)
    position: Mapped[int]
    phase: Mapped[RunLogPhase] = mapped_column(build_text_enum(RunLogPhase, "run_log_phase"))
    test_case_id: Mapped[UUID | None] = mapped_column(ForeignKey("test_cases.id"))
    kind: Mapped[RunLogEntryKind] = mapped_column(build_text_enum(RunLogEntryKind, "run_log_entry_kind"))
    at: Mapped[datetime]
    tool: Mapped[str | None]
    input: Mapped[JsonValue] = mapped_column(JSONB(none_as_null=True), nullable=True)
    output: Mapped[str | None] = mapped_column(Text)
    is_error: Mapped[bool]
    duration_ms: Mapped[int | None]
