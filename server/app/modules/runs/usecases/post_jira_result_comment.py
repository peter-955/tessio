from app.modules.jira import (
    JiraClient,
    JiraCommentJob,
    JiraCommentTrigger,
    JiraInvalidCredentialsError,
    JiraIssueRejectedError,
    JiraNotConfiguredError,
    JiraWriteNotAllowedError,
    LoadJiraCredentialsUseCase,
)
from app.modules.runs.ports.jira_comment_source_reader import JiraCommentSourceReader
from app.modules.runs.typing.enums import RunStatus
from app.modules.runs.utils.jira_result_comment import build_jira_result_comment
from app.shared.common import Transaction
from app.shared.logging import get_logger

log = get_logger(__name__)


class PostJiraResultCommentUseCase:
    def __init__(
        self,
        transaction: Transaction,
        jira_comment_source_reader: JiraCommentSourceReader,
        load_jira_credentials: LoadJiraCredentialsUseCase,
        jira_client: JiraClient,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._jira_comment_source_reader = jira_comment_source_reader
        self._load_jira_credentials = load_jira_credentials
        self._jira_client = jira_client
        self._client_url = client_url

    async def execute(self, job: JiraCommentJob) -> bool:
        async with self._transaction.begin():
            source = await self._jira_comment_source_reader.find(job.project_id, job.story_id, job.run_id)
        if source is None or not source.is_project_linked or not source.is_story_from_jira:
            log.info("jira.comment.skipped", extra={"story_id": str(job.story_id), "trigger": job.trigger.value})
            return False
        if job.trigger is JiraCommentTrigger.RUN_FINISHED and (
            source.run_id is None or source.run_status is RunStatus.ABORTED
        ):
            log.info("jira.comment.skipped", extra={"story_id": str(job.story_id), "trigger": job.trigger.value})
            return False
        try:
            credentials = await self._load_jira_credentials.execute()
            await self._jira_client.add_comment(
                credentials,
                source.story_jira_key,
                build_jira_result_comment(source, job.trigger, self._client_url),
            )
        except (
            JiraNotConfiguredError,
            JiraInvalidCredentialsError,
            JiraWriteNotAllowedError,
            JiraIssueRejectedError,
        ) as error:
            log.warning(
                "jira.comment.refused",
                extra={"story_id": str(job.story_id), "trigger": job.trigger.value, "error_code": error.code.value},
            )
            return False
        return True
