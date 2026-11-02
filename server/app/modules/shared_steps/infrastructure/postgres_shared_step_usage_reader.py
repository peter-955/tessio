from collections.abc import Collection
from uuid import UUID

from sqlalchemy import ColumnElement, Text, column, func, literal, select, true

from app.modules.shared_steps.domains.case_step_keys.entity import CaseStepKeys
from app.modules.shared_steps.domains.shared_step_usage.entity import SharedStepUsage
from app.modules.shared_steps.infrastructure.case_usage_tables import TEST_CASE_TABLE, TEST_CASE_VERSION_TABLE
from app.modules.shared_steps.ports.shared_step_usage_reader import SharedStepUsageReader
from app.modules.shared_steps.typing.constants import CASE_CODE_PREFIX, DEPRECATED_CASE_STATUS
from app.modules.stories.infrastructure import StoryTable
from app.shared.postgres import Database


class PostgresSharedStepUsageReader(SharedStepUsageReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def count_cases(self, project_id: UUID, keys: Collection[str]) -> dict[str, int]:
        if not keys:
            return {}
        step = func.jsonb_array_elements(TEST_CASE_VERSION_TABLE.c.steps).table_valued(column("value")).alias("step")
        step_key = step.c.value.op("->>")(literal("shared_step_key", Text))
        result = await self._database.get_current_session().execute(
            select(step_key, func.count(func.distinct(TEST_CASE_TABLE.c.id)))
            .select_from(TEST_CASE_TABLE)
            .join(TEST_CASE_VERSION_TABLE, TEST_CASE_VERSION_TABLE.c.id == TEST_CASE_TABLE.c.current_version_id)
            .join(step, true())
            .where(self._is_active_case(project_id), step_key.in_(sorted(keys)))
            .group_by(step_key)
        )
        return {key: int(count) for key, count in result}

    async def list_cases(self, project_id: UUID, key: str) -> list[SharedStepUsage]:
        result = await self._database.get_current_session().execute(
            select(
                TEST_CASE_TABLE.c.id,
                TEST_CASE_TABLE.c.number,
                TEST_CASE_TABLE.c.title,
                TEST_CASE_TABLE.c.status,
                StoryTable.jira_key,
                TEST_CASE_VERSION_TABLE.c.number,
            )
            .join(TEST_CASE_VERSION_TABLE, TEST_CASE_VERSION_TABLE.c.id == TEST_CASE_TABLE.c.current_version_id)
            .join(StoryTable, StoryTable.id == TEST_CASE_TABLE.c.story_id)
            .where(
                self._is_active_case(project_id),
                TEST_CASE_VERSION_TABLE.c.steps.contains([{"shared_step_key": key}]),
            )
            .order_by(TEST_CASE_TABLE.c.number)
        )
        return [
            SharedStepUsage(
                test_case_id=test_case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                title=title,
                status=status,
                story_jira_key=story_jira_key,
                version_number=version_number,
            )
            for test_case_id, number, title, status, story_jira_key, version_number in result
        ]

    async def list_case_step_keys(self, project_id: UUID, key: str) -> list[CaseStepKeys]:
        result = await self._database.get_current_session().execute(
            select(TEST_CASE_TABLE.c.number, TEST_CASE_VERSION_TABLE.c.steps)
            .join(TEST_CASE_VERSION_TABLE, TEST_CASE_VERSION_TABLE.c.id == TEST_CASE_TABLE.c.current_version_id)
            .where(
                self._is_active_case(project_id),
                TEST_CASE_VERSION_TABLE.c.steps.contains([{"shared_step_key": key}]),
            )
            .order_by(TEST_CASE_TABLE.c.number)
        )
        return [
            CaseStepKeys(
                code=f"{CASE_CODE_PREFIX}{number}",
                step_keys=[self._read_step_key(step) for step in steps],
            )
            for number, steps in result
        ]

    @staticmethod
    def _read_step_key(step: object) -> str | None:
        if not isinstance(step, dict) or step.get("action") is not None:
            return None
        step_key = step.get("shared_step_key")
        return step_key if isinstance(step_key, str) else None

    @staticmethod
    def _is_active_case(project_id: UUID) -> ColumnElement[bool]:
        return (TEST_CASE_TABLE.c.project_id == project_id) & (TEST_CASE_TABLE.c.status != DEPRECATED_CASE_STATUS)
