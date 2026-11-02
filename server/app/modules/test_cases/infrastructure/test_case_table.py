from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.test_cases.typing.enums import TestCasePriority, TestCaseStatus
from app.shared.postgres import TableBase, build_text_enum


class TestCaseTable(TableBase):
    __tablename__ = "test_cases"
    __table_args__ = (UniqueConstraint("project_id", "number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"), index=True)
    number: Mapped[int]
    title: Mapped[str] = mapped_column(Text)
    priority: Mapped[TestCasePriority] = mapped_column(build_text_enum(TestCasePriority, "test_case_priority"))
    status: Mapped[TestCaseStatus] = mapped_column(build_text_enum(TestCaseStatus, "test_case_status"))
    current_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("test_case_versions.id", name="test_cases_current_version_id_fkey", use_alter=True)
    )
    status_changed_at: Mapped[datetime | None]
    status_changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    needs_review_at: Mapped[datetime | None]
    needs_review_criterion_ids: Mapped[list[UUID]] = mapped_column(ARRAY(Uuid))
    reviewed_at: Mapped[datetime | None]
    reviewed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    flaky_score: Mapped[int] = mapped_column(server_default=text("0"))
    flaky_since: Mapped[datetime | None]
    disagreed_at: Mapped[datetime | None]
    quarantined_at: Mapped[datetime | None]
    quarantined_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", name="test_cases_quarantined_by_fkey"))
    quarantine_reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
