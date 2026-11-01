from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.notifications.typing.enums import NotificationKind
from app.shared.postgres import TableBase, build_text_enum


class NotificationTable(TableBase):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_id_id", "user_id", "id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[NotificationKind] = mapped_column(build_text_enum(NotificationKind, "notification_kind"))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB)
    read_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
