from collections.abc import Collection
from uuid import UUID

from sqlalchemy import select

from app.modules.stories.infrastructure import AcceptanceCriterionTable
from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.ports.criterion_reader import CriterionReader
from app.shared.postgres import Database


class PostgresCriterionReader(CriterionReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_story(self, story_id: UUID) -> list[CaseCriterion]:
        rows = await self._database.get_current_session().scalars(
            select(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.story_id == story_id)
            .order_by(AcceptanceCriterionTable.position)
        )
        return [self._to_criterion(row) for row in rows]

    async def list_by_ids(self, criterion_ids: Collection[UUID]) -> list[CaseCriterion]:
        rows = await self._database.get_current_session().scalars(
            select(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.id.in_(sorted(criterion_ids)))
            .order_by(AcceptanceCriterionTable.position)
        )
        return [self._to_criterion(row) for row in rows]

    @staticmethod
    def _to_criterion(row: AcceptanceCriterionTable) -> CaseCriterion:
        return CaseCriterion(
            id=row.id,
            story_id=row.story_id,
            code=row.code,
            text=row.text,
            position=row.position,
            is_removed=row.removed_at is not None,
        )
