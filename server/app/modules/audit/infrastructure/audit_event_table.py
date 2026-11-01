from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.audit.typing.enums import AuditAction
from app.shared.postgres import TableBase, build_text_enum


class AuditEventTable(TableBase):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_project_id_created_at", "project_id", "created_at"),
        Index("ix_audit_events_run_id_action", "run_id", "action"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    api_token_id: Mapped[UUID | None]
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id"))
    action: Mapped[AuditAction] = mapped_column(build_text_enum(AuditAction, "audit_action"))
    target_id: Mapped[UUID | None]
    run_id: Mapped[UUID | None]
    created_at: Mapped[datetime]
