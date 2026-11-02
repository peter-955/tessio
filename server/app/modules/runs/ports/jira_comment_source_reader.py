from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.jira_comment_source.entity import JiraCommentSource


class JiraCommentSourceReader(ABC):
    @abstractmethod
    async def find(self, project_id: UUID, story_id: UUID, run_id: UUID | None) -> JiraCommentSource | None: ...
