from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.plans.typing.constants import SUITE_OR_STORY_CHECK
from app.shared.postgres import TableBase


class TestPlanItemTable(TableBase):
    __tablename__ = "test_plan_items"
    __table_args__ = (
        CheckConstraint("(test_suite_id IS NULL) <> (story_id IS NULL)", name=SUITE_OR_STORY_CHECK),
        UniqueConstraint("test_plan_id", "test_suite_id"),
        UniqueConstraint("test_plan_id", "story_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    test_plan_id: Mapped[UUID] = mapped_column(ForeignKey("test_plans.id", ondelete="CASCADE"), index=True)
    test_suite_id: Mapped[UUID | None] = mapped_column(ForeignKey("test_suites.id"), index=True)
    story_id: Mapped[UUID | None] = mapped_column(ForeignKey("stories.id"), index=True)
    position: Mapped[int]
    created_at: Mapped[datetime]
