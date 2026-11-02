from uuid import UUID

from sqlalchemy import delete, select

from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.infrastructure.acceptance_criterion_table import AcceptanceCriterionTable
from app.shared.postgres import Database


class PostgresAcceptanceCriterionRepository(AcceptanceCriterionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_story(self, story_id: UUID) -> list[AcceptanceCriterion]:
        rows = await self._database.get_current_session().scalars(
            select(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.story_id == story_id)
            .order_by(AcceptanceCriterionTable.position)
        )
        return [AcceptanceCriterion.model_validate(row) for row in rows]

    async def save(self, criterion: AcceptanceCriterion) -> None:
        await self._database.get_current_session().merge(AcceptanceCriterionTable(**criterion.model_dump()))

    async def delete_for_story(self, story_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(AcceptanceCriterionTable).where(AcceptanceCriterionTable.story_id == story_id)
        )
