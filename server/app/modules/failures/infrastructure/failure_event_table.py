from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.runs import SuspectedCause
from app.shared.postgres import TableBase, build_text_enum


class FailureEventTable(TableBase):
    __tablename__ = "failure_events"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    failure_id: Mapped[UUID] = mapped_column(ForeignKey("failures.id"), index=True)
    kind: Mapped[FailureEventKind] = mapped_column(build_text_enum(FailureEventKind, "failure_event_kind"))
    from_status: Mapped[FailureStatus | None] = mapped_column(
        build_text_enum(FailureStatus, "failure_event_from_status")
    )
    to_status: Mapped[FailureStatus | None] = mapped_column(build_text_enum(FailureStatus, "failure_event_to_status"))
    from_cause: Mapped[SuspectedCause | None] = mapped_column(
        build_text_enum(SuspectedCause, "failure_event_from_cause")
    )
    to_cause: Mapped[SuspectedCause | None] = mapped_column(build_text_enum(SuspectedCause, "failure_event_to_cause"))
    case_result_id: Mapped[UUID | None] = mapped_column(ForeignKey("case_results.id"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]
    jira_issue_key: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(40))
