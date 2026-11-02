from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.integrations.domains.chat_failure_details.entity import ChatFailureDetails
from app.modules.integrations.domains.chat_gap_details.entity import ChatGapDetails
from app.modules.integrations.domains.chat_plan_details.entity import ChatPlanDetails
from app.modules.integrations.domains.chat_project.entity import ChatProject
from app.modules.integrations.domains.chat_run_details.entity import ChatRunDetails
from app.modules.integrations.domains.chat_story_details.entity import ChatStoryDetails


class ChatEventReader(ABC):
    @abstractmethod
    async def find_project(self, project_id: UUID) -> ChatProject | None: ...

    @abstractmethod
    async def find_run(self, project_id: UUID, run_id: UUID) -> ChatRunDetails | None: ...

    @abstractmethod
    async def find_failure(self, project_id: UUID, failure_id: UUID) -> ChatFailureDetails | None: ...

    @abstractmethod
    async def find_gap(self, project_id: UUID, gap_id: UUID) -> ChatGapDetails | None: ...

    @abstractmethod
    async def find_story(self, project_id: UUID, story_id: UUID) -> ChatStoryDetails | None: ...

    @abstractmethod
    async def find_plan(self, project_id: UUID, plan_id: UUID) -> ChatPlanDetails | None: ...
