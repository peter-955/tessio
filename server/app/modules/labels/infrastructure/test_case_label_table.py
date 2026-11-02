from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestCaseLabelTable(TableBase):
    __tablename__ = "test_case_labels"

    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"), primary_key=True)
    label_id: Mapped[UUID] = mapped_column(ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True, index=True)
    created_at: Mapped[datetime]
