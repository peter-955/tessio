from uuid import UUID

from sqlalchemy import exists, select

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.infrastructure.case_result_table import CaseResultTable
from app.modules.runs.infrastructure.step_result_table import StepResultTable
from app.shared.postgres import Database


class PostgresCaseResultRepository(CaseResultRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add(self, case_result: CaseResult, step_results: list[StepResult]) -> None:
        session = self._database.get_current_session()
        session.add(CaseResultTable(**case_result.model_dump()))
        await session.flush()
        session.add_all([StepResultTable(**step_result.model_dump()) for step_result in step_results])
        await session.flush()

    async def find_by_id(self, run_id: UUID, case_result_id: UUID) -> CaseResult | None:
        row = await self._database.get_current_session().scalar(
            select(CaseResultTable).where(CaseResultTable.run_id == run_id, CaseResultTable.id == case_result_id)
        )
        return None if row is None else CaseResult.model_validate(row)

    async def find_for_case(self, run_id: UUID, test_case_id: UUID) -> CaseResult | None:
        row = await self._database.get_current_session().scalar(
            select(CaseResultTable).where(
                CaseResultTable.run_id == run_id, CaseResultTable.test_case_id == test_case_id
            )
        )
        return None if row is None else CaseResult.model_validate(row)

    async def exists(self, run_id: UUID, test_case_id: UUID) -> bool:
        is_recorded = await self._database.get_current_session().scalar(
            select(exists().where(CaseResultTable.run_id == run_id, CaseResultTable.test_case_id == test_case_id))
        )
        return bool(is_recorded)

    async def list_for_run(self, run_id: UUID) -> list[CaseResult]:
        rows = await self._database.get_current_session().scalars(
            select(CaseResultTable)
            .where(CaseResultTable.run_id == run_id)
            .order_by(CaseResultTable.created_at, CaseResultTable.id)
        )
        return [CaseResult.model_validate(row) for row in rows]

    async def list_steps_for_run(self, run_id: UUID) -> list[StepResult]:
        rows = await self._database.get_current_session().scalars(
            select(StepResultTable)
            .join(CaseResultTable, CaseResultTable.id == StepResultTable.case_result_id)
            .where(CaseResultTable.run_id == run_id)
            .order_by(StepResultTable.case_result_id, StepResultTable.step_order)
        )
        return [StepResult.model_validate(row) for row in rows]
