from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class RunCaseTable(TableBase):
    __tablename__ = "run_cases"
    __table_args__ = (UniqueConstraint("run_id", "test_case_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("runs.id"))
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    test_case_version_id: Mapped[UUID] = mapped_column(ForeignKey("test_case_versions.id"))
    position: Mapped[int]
    created_at: Mapped[datetime]
    steps: Mapped[JsonValue | None] = mapped_column(JSONB, nullable=True)
