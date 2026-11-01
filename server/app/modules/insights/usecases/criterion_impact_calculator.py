from uuid import UUID

from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.typing.constants import FAILING_RESULT_STATUSES
from app.modules.insights.utils.coverage import build_criterion_traces
from app.modules.runs import CriterionImpact, CriterionImpactCalculator
from app.shared.common import Transaction


class LatestResultCriterionImpactCalculator(CriterionImpactCalculator):
    def __init__(self, transaction: Transaction, coverage_reader: CoverageReader) -> None:
        self._transaction = transaction
        self._coverage_reader = coverage_reader

    async def calculate(self, project_id: UUID, run_id: UUID) -> list[CriterionImpact]:
        async with self._transaction.begin():
            story_id = await self._coverage_reader.find_run_story_id(project_id, run_id)
            if story_id is None:
                return []
            criteria = await self._coverage_reader.list_criteria(project_id, [story_id])
            cases = await self._coverage_reader.list_cases(project_id, [story_id], False)
            outcomes = await self._coverage_reader.list_run_outcomes(project_id, run_id)
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
                )
            )
        return impacts
