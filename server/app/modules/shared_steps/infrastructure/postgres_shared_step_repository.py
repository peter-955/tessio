from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Select, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from app.modules.shared_steps.domains.current_shared_step.entity import CurrentSharedStep
from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step.repository import SharedStepRepository
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.modules.shared_steps.errors import SharedStepKeyAlreadyUsedError
from app.modules.shared_steps.infrastructure.shared_step_table import SharedStepTable
from app.modules.shared_steps.infrastructure.shared_step_version_table import SharedStepVersionTable
from app.modules.shared_steps.typing.constants import SHARED_STEP_KEY_CONSTRAINT
from app.shared.postgres import Database, read_constraint_name


class PostgresSharedStepRepository(SharedStepRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_key(self, project_id: UUID, key: str) -> SharedStep | None:
        row = await self._database.get_current_session().scalar(
            self._select_by_key(project_id, key).execution_options(populate_existing=True)
        )
        return None if row is None else SharedStep.model_validate(row)

    async def find_by_key_for_update(self, project_id: UUID, key: str) -> SharedStep | None:
        row = await self._database.get_current_session().scalar(
            self._select_by_key(project_id, key).with_for_update().execution_options(populate_existing=True)
        )
        return None if row is None else SharedStep.model_validate(row)

    async def find_version(self, version_id: UUID) -> SharedStepVersion | None:
        row = await self._database.get_current_session().scalar(
            select(SharedStepVersionTable)
            .where(SharedStepVersionTable.id == version_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else SharedStepVersion.model_validate(row)

    async def list_current(self, project_id: UUID, is_including_archived: bool) -> list[CurrentSharedStep]:
        statement = self._select_current(project_id)
        if not is_including_archived:
            statement = statement.where(SharedStepTable.archived_at.is_(None))
        return await self._list(statement)

    async def list_current_by_keys(self, project_id: UUID, keys: Collection[str]) -> list[CurrentSharedStep]:
        if not keys:
            return []
        return await self._list(self._select_current(project_id).where(SharedStepTable.key.in_(sorted(keys))))

    async def add(self, shared_step: SharedStep, version: SharedStepVersion) -> None:
        session = self._database.get_current_session()
        try:
            await session.execute(
                insert(SharedStepTable).values({**shared_step.model_dump(), "current_version_id": None})
            )
        except IntegrityError as error:
            if read_constraint_name(error) == SHARED_STEP_KEY_CONSTRAINT:
                raise SharedStepKeyAlreadyUsedError from error
            raise
        await self.add_version(shared_step, version)

    async def add_version(self, shared_step: SharedStep, version: SharedStepVersion) -> None:
        session = self._database.get_current_session()
        await session.execute(insert(SharedStepVersionTable).values(**version.model_dump()))
        await session.execute(
            update(SharedStepTable)
            .where(SharedStepTable.id == shared_step.id)
            .values(title=shared_step.title, archived_at=shared_step.archived_at, current_version_id=version.id)
        )

    async def save(self, shared_step: SharedStep) -> None:
        await self._database.get_current_session().execute(
            update(SharedStepTable)
            .where(SharedStepTable.id == shared_step.id)
            .values(title=shared_step.title, archived_at=shared_step.archived_at)
        )

    @staticmethod
    def _select_by_key(project_id: UUID, key: str) -> Select[SharedStepTable]:
        return select(SharedStepTable).where(SharedStepTable.project_id == project_id, SharedStepTable.key == key)

    @staticmethod
    def _select_current(project_id: UUID) -> Select[SharedStepTable, SharedStepVersionTable]:
        return (
            select(SharedStepTable, SharedStepVersionTable)
            .join(SharedStepVersionTable, SharedStepVersionTable.id == SharedStepTable.current_version_id)
            .where(SharedStepTable.project_id == project_id)
            .order_by(SharedStepTable.key)
            .execution_options(populate_existing=True)
        )

    async def _list(self, statement: Select[SharedStepTable, SharedStepVersionTable]) -> list[CurrentSharedStep]:
        result = await self._database.get_current_session().execute(statement)
        return [
            CurrentSharedStep(
                shared_step=SharedStep.model_validate(step_row), version=SharedStepVersion.model_validate(version_row)
            )
            for step_row, version_row in result
        ]
