from collections.abc import Collection
from uuid import UUID

from sqlalchemy import exists, select

from app.modules.plans.ports.plan_reference_reader import PlanReferenceReader
from app.modules.stories.infrastructure import StoryTable
from app.modules.suites.infrastructure import TestSuiteTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.postgres import Database


class PostgresPlanReferenceReader(PlanReferenceReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_active_environment(self, project_id: UUID, environment_id: UUID) -> bool:
        found = await self._database.get_current_session().scalar(
            select(
                exists().where(
                    EnvironmentTable.project_id == project_id,
                    EnvironmentTable.id == environment_id,
                    EnvironmentTable.archived_at.is_(None),
                )
            )
        )
        return bool(found)

    async def list_project_suite_ids(self, project_id: UUID, suite_ids: Collection[UUID]) -> set[UUID]:
        if not suite_ids:
            return set()
        found_ids = await self._database.get_current_session().scalars(
            select(TestSuiteTable.id).where(TestSuiteTable.project_id == project_id, TestSuiteTable.id.in_(suite_ids))
        )
        return set(found_ids)

    async def list_project_story_ids(self, project_id: UUID, story_ids: Collection[UUID]) -> set[UUID]:
        if not story_ids:
            return set()
        found_ids = await self._database.get_current_session().scalars(
            select(StoryTable.id).where(StoryTable.project_id == project_id, StoryTable.id.in_(story_ids))
        )
        return set(found_ids)
