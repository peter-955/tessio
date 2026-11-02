from uuid import UUID

from pydantic import JsonValue

from app.modules.failures.usecases.create_jira_issue import CreateJiraIssueUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class CreateJiraIssueJobHandler(JobHandler):
    def __init__(self, use_case: CreateJiraIssueUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        project_id = self._parse_uuid(data.get("projectId"))
        failure_id = self._parse_uuid(data.get("failureId"))
        if project_id is None or failure_id is None:
            log.warning("jira.create_issue.invalid_job_data", extra={"keys": sorted(data)})
            return
        await self._use_case.execute(project_id, failure_id, self._parse_uuid(data.get("requestedBy")))

    @staticmethod
    def _parse_uuid(value: JsonValue) -> UUID | None:
        if not isinstance(value, str):
            return None
        try:
            return UUID(value)
        except ValueError:
            return None
