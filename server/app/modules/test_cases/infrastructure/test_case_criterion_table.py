from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestCaseCriterionTable(TableBase):
    __tablename__ = "test_case_criteria"

    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"), primary_key=True)
    criterion_id: Mapped[UUID] = mapped_column(ForeignKey("acceptance_criteria.id"), primary_key=True, index=True)
    created_at: Mapped[datetime]
