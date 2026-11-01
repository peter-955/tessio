from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.runs.typing.enums import ResultStatus
from app.shared.postgres import TableBase, build_text_enum


class StepResultTable(TableBase):
    __tablename__ = "step_results"
    __table_args__ = (UniqueConstraint("case_result_id", "step_order"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    case_result_id: Mapped[UUID] = mapped_column(ForeignKey("case_results.id"))
    step_order: Mapped[int]
    status: Mapped[ResultStatus] = mapped_column(build_text_enum(ResultStatus, "step_result_status"))
    actual_result: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    screenshot_file_id: Mapped[UUID | None] = mapped_column(ForeignKey("stored_files.id"))
    evidence_file_id: Mapped[UUID | None] = mapped_column(ForeignKey("stored_files.id"))
    created_at: Mapped[datetime]
