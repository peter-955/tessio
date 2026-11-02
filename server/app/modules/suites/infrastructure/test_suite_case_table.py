from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestSuiteCaseTable(TableBase):
    __tablename__ = "test_suite_cases"

    test_suite_id: Mapped[UUID] = mapped_column(ForeignKey("test_suites.id", ondelete="CASCADE"), primary_key=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"), primary_key=True, index=True)
    position: Mapped[int]
    created_at: Mapped[datetime]
