from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, LargeBinary, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.users.typing.enums import ColorScheme, UserLanguage, UserStatus, WorkspaceRole
from app.shared.postgres import TableBase, build_text_enum


class UserTable(TableBase):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    workspace_role: Mapped[WorkspaceRole] = mapped_column(build_text_enum(WorkspaceRole, "workspace_role"))
    status: Mapped[UserStatus] = mapped_column(build_text_enum(UserStatus, "user_status"))
    password_hash: Mapped[str | None]
    totp_key_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    totp_confirmed_at: Mapped[datetime | None]
    totp_last_time_step: Mapped[int | None]
    failed_sign_ins: Mapped[int] = mapped_column(server_default=text("0"))
    locked_until: Mapped[datetime | None]
    created_at: Mapped[datetime]
    language: Mapped[UserLanguage] = mapped_column(build_text_enum(UserLanguage, "user_language"), server_default="en")
    color_scheme: Mapped[ColorScheme] = mapped_column(
        build_text_enum(ColorScheme, "color_scheme"), server_default="auto"
    )
    avatar_file_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("stored_files.id", name="users_avatar_file_id_fkey", use_alter=True)
    )
    deactivated_at: Mapped[datetime | None]
