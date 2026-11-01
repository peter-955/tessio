from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.postgres import TableBase


class RecoveryCodeTable(TableBase):
    __tablename__ = "recovery_codes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    code_hash: Mapped[str]
    used_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
