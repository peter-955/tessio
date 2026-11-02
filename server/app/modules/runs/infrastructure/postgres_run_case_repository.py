from uuid import UUID

from pydantic import JsonValue, TypeAdapter
from sqlalchemy import select

from app.modules.runs.domains.run_case.entity import RunCase
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.infrastructure.run_case_table import RunCaseTable
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases import TestCaseVersion, TestStep, parse_references
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.shared.postgres import Database

STEPS_ADAPTER = TypeAdapter(list[TestStep])


class PostgresRunCaseRepository(RunCaseRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add_all(self, run_cases: list[RunCase]) -> None:
        self._database.get_current_session().add_all([RunCaseTable(**run_case.model_dump()) for run_case in run_cases])

    async def list_for_run(self, run_id: UUID) -> list[RunCase]:
        rows = await self._database.get_current_session().scalars(
            select(RunCaseTable).where(RunCaseTable.run_id == run_id).order_by(RunCaseTable.position)
        )
        return [RunCase.model_validate(row) for row in rows]

    async def list_views(self, run_id: UUID) -> list[RunCaseView]:
        result = await self._database.get_current_session().execute(
            select(
                RunCaseTable.test_case_id,
                RunCaseTable.position,
                RunCaseTable.steps,
                TestCaseTable.number,
                TestCaseVersionTable,
                StoryTable.id,
                StoryTable.jira_key,
                StoryTable.title,
            )
            .join(TestCaseTable, TestCaseTable.id == RunCaseTable.test_case_id)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == RunCaseTable.test_case_version_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(RunCaseTable.run_id == run_id)
            .order_by(RunCaseTable.position)
        )
        return [
            RunCaseView(
                test_case_id=test_case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                position=position,
                version=self._apply_snapshot(TestCaseVersion.model_validate(version_row), snapshot_steps),
                story_id=story_id,
                story_jira_key=story_jira_key,
                story_title=story_title,
            )
            for test_case_id, position, snapshot_steps, number, version_row, story_id, story_jira_key, story_title in (
                result
            )
        ]

    @staticmethod
    def _apply_snapshot(version: TestCaseVersion, snapshot_steps: JsonValue | None) -> TestCaseVersion:
        if snapshot_steps is None:
            return version
        steps = STEPS_ADAPTER.validate_python(snapshot_steps)
        references = parse_references(version.preconditions, steps, version.data_rows)
        return version.model_copy(
            update={"steps": steps, "data_keys": sorted(references.data_keys | set(version.data_keys))}
        )
