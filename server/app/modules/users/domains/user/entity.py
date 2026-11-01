from datetime import datetime
from uuid import UUID

from app.modules.users.typing.enums import ColorScheme, UserLanguage, UserStatus, WorkspaceRole
from app.shared.common import Entity


class User(Entity):
    id: UUID
    email: str
    name: str
    workspace_role: WorkspaceRole
    status: UserStatus
    password_hash: str | None
    totp_key_encrypted: bytes | None
    totp_confirmed_at: datetime | None
    totp_last_time_step: int | None
    failed_sign_ins: int
    locked_until: datetime | None
    created_at: datetime
    language: UserLanguage = UserLanguage.EN
    color_scheme: ColorScheme = ColorScheme.AUTO
    avatar_file_id: UUID | None = None
    deactivated_at: datetime | None = None

    @property
    def is_two_factor_set_up(self) -> bool:
        return self.totp_confirmed_at is not None

    @property
    def can_manage_workspace(self) -> bool:
        return self.workspace_role in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}

    def is_locked(self, now: datetime) -> bool:
        return self.locked_until is not None and now < self.locked_until
