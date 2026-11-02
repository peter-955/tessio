from collections.abc import Collection
from uuid import UUID

from redis.exceptions import RedisError
from sqlalchemy import select

from app.modules.jira.domains.jira_comment_job.entity import JiraCommentJob
from app.modules.jira.ports.jira_result_comment_requester import JiraResultCommentRequester
from app.modules.jira.typing.constants import JIRA_COMMENT_JOB_ID_TEMPLATE
from app.modules.jira.typing.enums import JiraCommentTrigger
from app.modules.jira.utils.jira_comment_job import build_jira_comment_job_data
from app.modules.jira.utils.jira_post_results import is_posting_results
from app.modules.projects.infrastructure import ProjectTable
from app.shared.logging import get_logger
from app.shared.postgres import Database
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class QueuedJiraResultCommentRequester(JiraResultCommentRequester):
    def __init__(self, database: Database, job_queue: JobQueue) -> None:
        self._database = database
        self._job_queue = job_queue

    async def request_after_sign_off(self, project_id: UUID, story_id: UUID) -> None:
        if not await self._is_posting(project_id, JiraCommentTrigger.SIGN_OFF):
            return
        await self._enqueue(
            JiraCommentJob(trigger=JiraCommentTrigger.SIGN_OFF, project_id=project_id, story_id=story_id, run_id=None),
            None,
        )

    async def request_after_run(self, project_id: UUID, run_id: UUID, story_ids: Collection[UUID]) -> None:
        if not story_ids or not await self._is_posting(project_id, JiraCommentTrigger.RUN_FINISHED):
            return
        for story_id in sorted(set(story_ids)):
            await self._enqueue(
                JiraCommentJob(
                    trigger=JiraCommentTrigger.RUN_FINISHED, project_id=project_id, story_id=story_id, run_id=run_id
                ),
                JIRA_COMMENT_JOB_ID_TEMPLATE.format(run_id=run_id, story_id=story_id),
            )

    async def _is_posting(self, project_id: UUID, trigger: JiraCommentTrigger) -> bool:
        async with self._database.begin():
            row = (
                await self._database.get_current_session().execute(
                    select(ProjectTable.jira_project_key, ProjectTable.jira_post_results).where(
                        ProjectTable.id == project_id
                    )
                )
            ).one_or_none()
        if row is None or row.jira_project_key is None:
            return False
        return is_posting_results(row.jira_post_results, trigger)

    async def _enqueue(self, job: JiraCommentJob, job_id: str | None) -> None:
        try:
            await self._job_queue.add(
                QueueName.JIRA, JobName.JIRA_POST_COMMENT, build_jira_comment_job_data(job), job_id=job_id
            )
        except RedisError as error:
            log.warning(
                "jira.comment_enqueue_failed",
                extra={"story_id": str(job.story_id), "trigger": job.trigger.value, "reason": type(error).__name__},
            )
