from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.test_cases.typing.enums import QuarantineEventKind
from app.shared.postgres import TableBase, build_text_enum


class TestCaseQuarantineEventTable(TableBase):
    __tablename__ = "test_case_quarantine_events"
    __table_args__ = (Index("ix_test_case_quarantine_events_test_case_id_created_at", "test_case_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    test_case_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.id"))
    kind: Mapped[QuarantineEventKind] = mapped_column(build_text_enum(QuarantineEventKind, "quarantine_event_kind"))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime]
