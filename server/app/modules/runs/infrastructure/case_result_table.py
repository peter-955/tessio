from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.runs.typing.enums import ResultStatus
from app.shared.postgres import TableBase, build_text_enum


class CaseResultTable(TableBase):
    __tablename__ = "case_results"
    __table_args__ = (
        UniqueConstraint("run_id", "test_case_id"),
        Index("ix_case_results_test_case_id_created_at", "test_case_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("runs.id"))
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    test_case_version_id: Mapped[UUID] = mapped_column(ForeignKey("test_case_versions.id"))
    status: Mapped[ResultStatus] = mapped_column(build_text_enum(ResultStatus, "case_result_status"))
    duration_ms: Mapped[int | None]
    recorded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
