from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.users.domains.user.entity import User
from app.modules.users.typing.enums import UserStatus, WorkspaceRole


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_id_for_update(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def update(self, current: User, updated: User) -> None: ...

    @abstractmethod
    async def list(
        self, status: UserStatus | None, workspace_role: WorkspaceRole | None, query: str | None
    ) -> list[User]: ...
