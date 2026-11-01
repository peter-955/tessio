from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.auth.domains.avatar_file.entity import AvatarFile


class AvatarFileReader(ABC):
    @abstractmethod
    async def find(self, file_id: UUID) -> AvatarFile | None: ...
