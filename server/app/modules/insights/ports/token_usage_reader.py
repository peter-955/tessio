from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.insights.domains.token_run.entity import TokenRun


class TokenUsageReader(ABC):
    @abstractmethod
    async def list_token_runs(
        self, project_id: UUID, start_at: datetime, end_at: datetime, limit: int
    ) -> list[TokenRun]: ...
