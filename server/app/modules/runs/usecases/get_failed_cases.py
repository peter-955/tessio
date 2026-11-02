from uuid import UUID

from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.failed_case.entity import FailedCase
from app.modules.runs.domains.failed_cases.entity import FailedCases
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.errors import EnvironmentNotFoundError, RunNotFoundError
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.typing.constants.run_report import FAILING_RESULT_STATUSES
from app.modules.runs.utils.run_target import find_run_target
from app.modules.runs.utils.worst_iteration import select_worst_results
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetFailedCasesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_target_reader: RunTargetReader,
        run_story_reader: RunStoryReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_target_reader = run_target_reader
        self._run_story_reader = run_story_reader

    async def execute(self, actor: Actor, run_id: UUID) -> FailedCases:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_VIEW)
            run = await self._run_repository.find_by_id(access.project_id, run_id)
            if run is None:
                raise RunNotFoundError
            target = await find_run_target(run, self._run_story_reader)
            environment = await self._run_target_reader.find_environment_by_id(run.project_id, run.environment_id)
            if environment is None:
                raise EnvironmentNotFoundError(str(run.environment_id))
            run_cases = await self._run_case_repository.list_views(run.id)
            results_by_case_id = select_worst_results(await self._case_result_repository.list_for_run(run.id))
        return FailedCases(
            run=run,
            story_jira_key=target.story_jira_key,
            environment_name=environment.name,
            cases=[
                FailedCase(
                    test_case_id=run_case.test_case_id,
                    code=run_case.code,
                    title=run_case.version.title,
                    status=case_result.status,
                    story_jira_key=run_case.story_jira_key,
                )
                for run_case in run_cases
                if (case_result := results_by_case_id.get(run_case.test_case_id)) is not None
                and case_result.status in FAILING_RESULT_STATUSES
            ],
            suite_name=target.suite_name,
        )
