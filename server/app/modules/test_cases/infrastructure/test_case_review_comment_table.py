from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class TestCaseReviewCommentTable(TableBase):
    __tablename__ = "test_case_review_comments"
    __table_args__ = (CheckConstraint("step_order >= 1", name="ck_test_case_review_comments_step_order"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"), index=True)
    version_id: Mapped[UUID] = mapped_column(ForeignKey("test_case_versions.id"))
    step_order: Mapped[int | None]
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
    resolved_at: Mapped[datetime | None]
    resolved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
