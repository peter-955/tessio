from uuid import UUID

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.failures.domains.jira_bug_content.entity import JiraBugContent
from app.modules.failures.errors import FailureNotFoundError, FailureProjectWithoutJiraError
from app.modules.failures.ports.case_result_reader import CaseResultReader
from app.modules.failures.ports.jira_bug_source_reader import JiraBugSourceReader
from app.modules.failures.utils.jira_bug_content import build_jira_bug_content
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class PreviewJiraIssueUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        failure_repository: FailureRepository,
        jira_bug_source_reader: JiraBugSourceReader,
        case_result_reader: CaseResultReader,
        secret_value_reader: SecretValueReader,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._failure_repository = failure_repository
        self._jira_bug_source_reader = jira_bug_source_reader
        self._case_result_reader = case_result_reader
        self._secret_value_reader = secret_value_reader
        self._client_url = client_url

    async def execute(self, actor: Actor, project_key: str, failure_id: UUID) -> JiraBugContent:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FAILURE_VIEW)
            view = await self._failure_repository.find_view(access.project_id, failure_id)
            if view is None:
                raise FailureNotFoundError
            source = await self._jira_bug_source_reader.find(view.failure)
            if source is None:
                raise FailureNotFoundError
            failed_step = await self._case_result_reader.find_failed_step(view.failure.latest_case_result_id)
        if source.jira_project_key is None:
            raise FailureProjectWithoutJiraError
        masker = SecretMasker(
            await self._secret_value_reader.list_secret_values(access.project_id, source.environment_id)
        )
        return build_jira_bug_content(source, source.jira_project_key, failed_step, self._client_url, masker)
