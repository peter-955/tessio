from abc import ABC, abstractmethod

from app.modules.jira.domains.jira_connection.entity import JiraConnection
from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess


class JiraConnectionRepository(ABC):
    @abstractmethod
    async def find(self) -> JiraConnection | None: ...

    @abstractmethod
    async def save(self, connection: JiraConnection) -> None: ...

    @abstractmethod
    async def save_write_access(self, write_access: JiraWriteAccess) -> None: ...
