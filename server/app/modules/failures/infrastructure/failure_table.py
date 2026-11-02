from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.failures.typing.enums import FailureStatus
from app.modules.runs import SuspectedCause
from app.shared.postgres import TableBase, build_text_enum


class FailureTable(TableBase):
    __tablename__ = "failures"
    __table_args__ = (
        Index(
            "uq_failures_test_case_id_active",
            "test_case_id",
            unique=True,
            postgresql_where=text("status <> 'verified'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    story_id: Mapped[UUID] = mapped_column(ForeignKey("stories.id"), index=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    opened_by_case_result_id: Mapped[UUID] = mapped_column(ForeignKey("case_results.id"))
    latest_case_result_id: Mapped[UUID] = mapped_column(ForeignKey("case_results.id"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[FailureStatus] = mapped_column(build_text_enum(FailureStatus, "failure_status"))
    status_changed_at: Mapped[datetime | None]
    status_changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    cause: Mapped[SuspectedCause | None] = mapped_column(build_text_enum(SuspectedCause, "failure_cause"))
    cause_reason: Mapped[str | None] = mapped_column(Text)
    cause_changed_at: Mapped[datetime | None]
    cause_changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
    jira_issue_key: Mapped[str | None] = mapped_column(Text)
    jira_issue_url: Mapped[str | None] = mapped_column(Text)
    jira_issue_status: Mapped[str | None] = mapped_column(Text)
    jira_issue_done_at: Mapped[datetime | None]
    jira_issue_requested_at: Mapped[datetime | None]
    jira_issue_error_code: Mapped[str | None] = mapped_column(String(40))
