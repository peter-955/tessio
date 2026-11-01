from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.shared.postgres import TableBase, build_text_enum


class OneTimeTokenTable(TableBase):
    __tablename__ = "one_time_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    purpose: Mapped[OneTimeTokenPurpose] = mapped_column(build_text_enum(OneTimeTokenPurpose, "one_time_token_purpose"))
    token_hash: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
