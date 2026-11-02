from pydantic import JsonValue

from app.modules.jira import parse_jira_comment_job_data
from app.modules.runs.usecases.post_jira_result_comment import PostJiraResultCommentUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class PostJiraResultCommentJobHandler(JobHandler):
    def __init__(self, use_case: PostJiraResultCommentUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        job = parse_jira_comment_job_data(data)
        if job is None:
            log.warning("jira.comment.invalid_job_data", extra={"keys": sorted(data)})
            return
        await self._use_case.execute(job)
