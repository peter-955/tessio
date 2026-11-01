from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class UserSessionTable(TableBase):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(unique=True)
    is_two_factor_passed: Mapped[bool]
    user_agent: Mapped[str | None]
    ip: Mapped[str | None]
    last_seen_at: Mapped[datetime]
    expires_at: Mapped[datetime] = mapped_column(index=True)
    created_at: Mapped[datetime]
