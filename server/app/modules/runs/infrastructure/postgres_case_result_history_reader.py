from datetime import datetime
from uuid import UUID

from sqlalchemy import ColumnElement, Select, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.runs.infrastructure.case_result_table import CaseResultTable
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.infrastructure.worst_iteration_condition import is_worst_iteration
from app.modules.runs.typing.enums import ResultStatus, RunExecutor
from app.modules.test_cases import CaseResultHistoryReader, DecisiveResult, ResultExecutorKind
from app.shared.postgres import Database

DECISIVE_STATUSES = (ResultStatus.PASSED, ResultStatus.FAILED)


class PostgresCaseResultHistoryReader(CaseResultHistoryReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_version_results(self, test_case_id: UUID, version_id: UUID, limit: int) -> list[DecisiveResult]:
        return await self._list(
            self._select_decisive(test_case_id, CaseResultTable.test_case_version_id == version_id).limit(limit)
        )

    async def list_results_since(self, test_case_id: UUID, since: datetime, limit: int) -> list[DecisiveResult]:
        return await self._list(self._select_decisive(test_case_id, CaseResultTable.created_at > since).limit(limit))

    async def find_latest_per_executor_kind(
        self, test_case_id: UUID, version_id: UUID
    ) -> dict[ResultExecutorKind, DecisiveResult]:
        is_manual = RunTable.executor == RunExecutor.MANUAL
        statement = (
            self._select_decisive(test_case_id, CaseResultTable.test_case_version_id == version_id)
            .ext(distinct_on(is_manual))
            .order_by(None)
            .order_by(is_manual, CaseResultTable.created_at.desc(), CaseResultTable.id.desc())
        )
        return {result.executor_kind: result for result in await self._list(statement)}

    @staticmethod
    def _select_decisive(
        test_case_id: UUID, condition: ColumnElement[bool]
    ) -> Select[UUID, UUID, ResultStatus, RunExecutor, datetime]:
        return (
            select(
                CaseResultTable.id,
                CaseResultTable.test_case_version_id,
                CaseResultTable.status,
                RunTable.executor,
                CaseResultTable.created_at,
            )
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .where(
                CaseResultTable.test_case_id == test_case_id,
                CaseResultTable.status.in_(DECISIVE_STATUSES),
                is_worst_iteration(DECISIVE_STATUSES),
                condition,
            )
            .order_by(CaseResultTable.created_at.desc(), CaseResultTable.id.desc())
        )

    async def _list(self, statement: Select[UUID, UUID, ResultStatus, RunExecutor, datetime]) -> list[DecisiveResult]:
        result = await self._database.get_current_session().execute(statement)
        return [
            DecisiveResult(
                case_result_id=case_result_id,
                test_case_version_id=version_id,
                is_passed=status is ResultStatus.PASSED,
                executor_kind=ResultExecutorKind.MANUAL
                if executor is RunExecutor.MANUAL
                else ResultExecutorKind.AUTOMATED,
                recorded_at=recorded_at,
            )
            for case_result_id, version_id, status, executor, recorded_at in result
        ]
