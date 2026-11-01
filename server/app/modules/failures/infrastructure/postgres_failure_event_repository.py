from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event.repository import FailureEventRepository
from app.modules.failures.domains.failure_event_view.entity import FailureEventView
from app.modules.failures.infrastructure.failure_event_table import FailureEventTable
from app.modules.runs.infrastructure import CaseResultTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresFailureEventRepository(FailureEventRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add(self, event: FailureEvent) -> None:
        session = self._database.get_current_session()
        session.add(FailureEventTable(**event.model_dump()))
        await session.flush()

    async def list_views(self, failure_id: UUID) -> list[FailureEventView]:
        assignee = aliased(UserTable)
        actor = aliased(UserTable)
        result = await self._database.get_current_session().execute(
            select(FailureEventTable, CaseResultTable.run_id, assignee.name, actor.name)
            .outerjoin(CaseResultTable, CaseResultTable.id == FailureEventTable.case_result_id)
            .outerjoin(assignee, assignee.id == FailureEventTable.assignee_id)
            .outerjoin(actor, actor.id == FailureEventTable.actor_id)
            .where(FailureEventTable.failure_id == failure_id)
            .order_by(FailureEventTable.created_at, FailureEventTable.id)
        )
        return [
            FailureEventView(
                event=FailureEvent.model_validate(event_row),
                run_id=run_id,
                assignee_name=assignee_name,
                actor_name=actor_name,
            )
            for event_row, run_id, assignee_name, actor_name in result
        ]
