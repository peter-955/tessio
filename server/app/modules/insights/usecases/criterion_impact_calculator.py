from uuid import UUID

from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.typing.constants import FAILING_RESULT_STATUSES
from app.modules.insights.utils.coverage import build_criterion_traces
from app.modules.runs import CriterionImpact, CriterionImpactCalculator, ResultStatus
from app.shared.common import Transaction


class LatestResultCriterionImpactCalculator(CriterionImpactCalculator):
    def __init__(self, transaction: Transaction, coverage_reader: CoverageReader) -> None:
        self._transaction = transaction
        self._coverage_reader = coverage_reader

    async def calculate(self, project_id: UUID, run_id: UUID) -> list[CriterionImpact]:
        async with self._transaction.begin():
            story_id = await self._coverage_reader.find_run_story_id(project_id, run_id)
            story_keys = (
                {} if story_id is not None else await self._coverage_reader.list_run_case_story_keys(project_id, run_id)
            )
            story_ids = [story_id] if story_id is not None else list(story_keys)
            if not story_ids:
                return []
            criteria = await self._coverage_reader.list_criteria(project_id, story_ids)
            cases = await self._coverage_reader.list_cases(project_id, story_ids, False)
            outcomes = await self._coverage_reader.list_run_outcomes(project_id, run_id)
        impacts = self._build_impacts(criteria, cases, outcomes, story_keys)
        if story_id is not None:
            return impacts
        story_order = {jira_key: position for position, jira_key in enumerate(story_keys.values())}
        return sorted(
            (impact for impact in impacts if impact.run_case_codes),
            key=lambda impact: story_order.get(impact.story_jira_key or "", 0),
        )

    @staticmethod
    def _build_impacts(
        criteria: list[TracedCriterion],
        cases: list[TracedCase],
        outcomes: dict[UUID, ResultStatus | None],
        story_keys: dict[UUID, str],
    ) -> list[CriterionImpact]:
        codes_by_case_id = {case.id: case.code for case in cases}
        active_criteria = [criterion for criterion in criteria if criterion.is_active]
        impacts: list[CriterionImpact] = []
        for trace in build_criterion_traces(active_criteria, cases):
            run_case_ids = [case_id for case_id in trace.linked_case_ids if case_id in outcomes]
            impacts.append(
                CriterionImpact(
                    criterion_id=trace.criterion.id,
                    code=trace.criterion.code,
                    text=trace.criterion.text,
                    status=trace.status,
                    run_case_codes=[codes_by_case_id[case_id] for case_id in run_case_ids],
                    failed_case_codes=[
                        codes_by_case_id[case_id]
                        for case_id in run_case_ids
                        if outcomes[case_id] in FAILING_RESULT_STATUSES
                    ],
                    story_jira_key=story_keys.get(trace.criterion.story_id),
                )
            )
        return impacts
