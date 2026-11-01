from abc import ABC, abstractmethod

from app.modules.jira.domains.jira_connection.entity import JiraConnection


class JiraConnectionRepository(ABC):
    @abstractmethod
    async def find(self) -> JiraConnection | None: ...

    @abstractmethod
    async def save(self, connection: JiraConnection) -> None: ...
