from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.jira import JiraCredentials


class JiraIssueStatusRefresher(ABC):
    @abstractmethod
    async def refresh(self, project_id: UUID, credentials: JiraCredentials, now: datetime) -> None: ...
