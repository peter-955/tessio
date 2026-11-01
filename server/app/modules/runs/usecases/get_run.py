from collections import defaultdict
from uuid import UUID

from app.modules.files import StoredFileStatus
from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_case_detail.entity import RunCaseDetail
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.run_detail.entity import RunDetail
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.modules.runs.errors import RunNotFoundError
from app.modules.runs.ports.run_view_reader import RunViewReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_view_reader: RunViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_view_reader = run_view_reader

    async def execute(self, actor: Actor, project_key: str, run_id: UUID) -> RunDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_VIEW)
            run = await self._run_repository.find_by_id(access.project_id, run_id)
            if run is None:
                raise RunNotFoundError
            labels = await self._run_view_reader.find_labels(run)
            run_cases = await self._run_case_repository.list_views(run.id)
            case_results = await self._case_result_repository.list_for_run(run.id)
            step_results = await self._case_result_repository.list_steps_for_run(run.id)
            screenshot_statuses = await self._run_view_reader.list_screenshot_statuses(run.id)
            child_run_ids = await self._run_view_reader.list_child_run_ids(run.id)
        results_by_case_id = {case_result.test_case_id: case_result for case_result in case_results}
        steps_by_case_result_id: defaultdict[UUID, dict[int, StepResult]] = defaultdict(dict)
        for step_result in step_results:
            steps_by_case_result_id[step_result.case_result_id][step_result.step_order] = step_result
        return RunDetail(
            run=run,
            labels=labels,
            cases=[
                self._build_case_detail(
                    run_case,
                    results_by_case_id.get(run_case.test_case_id),
                    steps_by_case_result_id,
                    screenshot_statuses,
                )
                for run_case in run_cases
            ],
            child_run_ids=child_run_ids,
        )

    @staticmethod
    def _build_case_detail(
        run_case: RunCaseView,
        case_result: CaseResult | None,
        steps_by_case_result_id: defaultdict[UUID, dict[int, StepResult]],
        screenshot_statuses: dict[UUID, StoredFileStatus],
    ) -> RunCaseDetail:
        step_results = {} if case_result is None else steps_by_case_result_id[case_result.id]
        step_views: list[StepResultView] = []
        for step in sorted(run_case.version.steps, key=lambda version_step: version_step.order):
            step_result = step_results.get(step.order)
            screenshot_file_id = None if step_result is None else step_result.screenshot_file_id
            screenshot_status = None if screenshot_file_id is None else screenshot_statuses.get(screenshot_file_id)
            step_views.append(
                StepResultView(
                    step=step,
                    result=step_result,
                    screenshot_status=screenshot_status,
                )
            )
        return RunCaseDetail(view=run_case, result=case_result, steps=step_views)
