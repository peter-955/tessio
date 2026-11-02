from uuid import UUID

from sqlalchemy import insert, select

from app.modules.test_cases.domains.quarantine_event.entity import QuarantineEvent
from app.modules.test_cases.domains.quarantine_event.repository import QuarantineEventRepository
from app.modules.test_cases.domains.quarantine_event_view.entity import QuarantineEventView
from app.modules.test_cases.infrastructure.test_case_quarantine_event_table import TestCaseQuarantineEventTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresQuarantineEventRepository(QuarantineEventRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add(self, event: QuarantineEvent) -> None:
        await self._database.get_current_session().execute(
            insert(TestCaseQuarantineEventTable).values(**event.model_dump())
        )

    async def list_views(self, test_case_id: UUID) -> list[QuarantineEventView]:
        result = await self._database.get_current_session().execute(
            select(TestCaseQuarantineEventTable, UserTable.name)
            .outerjoin(UserTable, UserTable.id == TestCaseQuarantineEventTable.actor_id)
            .where(TestCaseQuarantineEventTable.test_case_id == test_case_id)
            .order_by(TestCaseQuarantineEventTable.created_at.desc(), TestCaseQuarantineEventTable.id.desc())
        )
        return [
            QuarantineEventView(event=QuarantineEvent.model_validate(row), actor_name=actor_name)
            for row, actor_name in result
        ]
