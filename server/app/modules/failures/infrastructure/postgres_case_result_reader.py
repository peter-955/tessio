from uuid import UUID

from sqlalchemy import select

from app.modules.failures.domains.case_result_history_item.entity import CaseResultHistoryItem
from app.modules.failures.domains.failed_step.entity import FailedStep
from app.modules.failures.ports.case_result_reader import CaseResultReader
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable, StepResultTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresCaseResultReader(CaseResultReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_failed_step(self, case_result_id: UUID) -> FailedStep | None:
        row = await self._database.get_current_session().scalar(
            select(StepResultTable)
            .where(StepResultTable.case_result_id == case_result_id, StepResultTable.status == ResultStatus.FAILED)
            .order_by(StepResultTable.step_order)
            .limit(1)
        )
        if row is None:
            return None
        return FailedStep(
            step_order=row.step_order,
            actual_result=row.actual_result or "",
            error=row.error,
            screenshot_file_id=row.screenshot_file_id,
        )

    async def list_history(
        self, test_case_id: UUID, since_case_result_id: UUID, limit: int
    ) -> list[CaseResultHistoryItem]:
        opened_at = (
            select(CaseResultTable.created_at).where(CaseResultTable.id == since_case_result_id).scalar_subquery()
        )
        result = await self._database.get_current_session().execute(
            select(
                CaseResultTable.id,
                CaseResultTable.run_id,
                RunTable.status,
                RunTable.executor,
                CaseResultTable.status,
                CaseResultTable.duration_ms,
                CaseResultTable.created_at,
                UserTable.name,
            )
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .join(UserTable, UserTable.id == RunTable.started_by)
            .where(CaseResultTable.test_case_id == test_case_id, CaseResultTable.created_at >= opened_at)
            .order_by(CaseResultTable.created_at.desc(), CaseResultTable.id.desc())
            .limit(limit)
        )
        return [
            CaseResultHistoryItem(
                case_result_id=case_result_id,
                run_id=run_id,
                run_status=run_status,
                run_executor=run_executor,
                status=status,
                duration_ms=duration_ms,
                recorded_at=recorded_at,
                started_by_name=started_by_name,
            )
            for (
                case_result_id,
                run_id,
                run_status,
                run_executor,
                status,
                duration_ms,
                recorded_at,
                started_by_name,
            ) in result
        ]
