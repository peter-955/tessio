from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.notifications.typing.enums import NotificationChannel, NotificationKind
from app.shared.postgres import TableBase, build_text_enum


class NotificationPreferenceTable(TableBase):
    __tablename__ = "notification_preferences"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    kind: Mapped[NotificationKind] = mapped_column(
        build_text_enum(NotificationKind, "notification_preference_kind"), primary_key=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        build_text_enum(NotificationChannel, "notification_channel"), primary_key=True
    )
    is_enabled: Mapped[bool]
