from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.api_tokens.typing.constants import MAXIMUM_PLUGIN_VERSION_LENGTH
from app.modules.api_tokens.typing.enums import ApiTokenScope
from app.shared.postgres import TableBase, build_text_enum


class ApiTokenTable(TableBase):
    __tablename__ = "api_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str]
    prefix: Mapped[str]
    token_hash: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime]
    last_used_at: Mapped[datetime | None]
    plugin_version: Mapped[str | None] = mapped_column(String(MAXIMUM_PLUGIN_VERSION_LENGTH))
    revoked_at: Mapped[datetime | None]
    created_at: Mapped[datetime]
    scope: Mapped[ApiTokenScope] = mapped_column(
        build_text_enum(ApiTokenScope, "api_token_scope"), server_default=text("'mcp'")
    )
