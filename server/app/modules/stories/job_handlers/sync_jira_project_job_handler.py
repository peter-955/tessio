from datetime import UTC, datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.stories.usecases.sync_jira_project import SyncJiraProjectUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class SyncJiraProjectJobHandler(JobHandler):
    def __init__(self, use_case: SyncJiraProjectUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        project_id_value = data.get("projectId")
        try:
            project_id = UUID(project_id_value) if isinstance(project_id_value, str) else None
        except ValueError:
            project_id = None
        if project_id is None:
            log.warning("jira_sync.invalid_job_data", extra={"project_id": str(project_id_value)})
            return
        await self._use_case.execute(project_id, datetime.now(UTC))
