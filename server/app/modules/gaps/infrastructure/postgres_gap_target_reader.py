import re
from collections.abc import Mapping
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import select

from app.modules.gaps.domains.gap_case.entity import GapCase
from app.modules.gaps.domains.gap_story.entity import GapStory
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.constants import TEST_CASE_CODE_PATTERN, TEST_CASE_CODE_PREFIX
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_cases import TestStep
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.shared.postgres import Database

STEPS_ADAPTER = TypeAdapter(list[TestStep])


class PostgresGapTargetReader(GapTargetReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_story(self, project_id: UUID, jira_key: str) -> GapStory | None:
        result = await self._database.get_current_session().execute(
            select(StoryTable.id, StoryTable.jira_key, StoryTable.title).where(
                StoryTable.project_id == project_id, StoryTable.jira_key == jira_key.strip().upper()
            )
        )
        row = result.one_or_none()
        if row is None:
            return None
        story_id, story_jira_key, title = row
        return GapStory(id=story_id, jira_key=story_jira_key, title=title)

    async def find_criterion_id(self, story_id: UUID, code: str) -> UUID | None:
        criterion_id: UUID | None = await self._database.get_current_session().scalar(
            select(AcceptanceCriterionTable.id).where(
                AcceptanceCriterionTable.story_id == story_id,
                AcceptanceCriterionTable.code == code.strip().upper(),
                AcceptanceCriterionTable.removed_at.is_(None),
            )
        )
        return criterion_id

    async def find_test_case_id(self, story_id: UUID, code: str) -> UUID | None:
        code_match = re.match(TEST_CASE_CODE_PATTERN, code.strip())
        if code_match is None:
            return None
        test_case_id: UUID | None = await self._database.get_current_session().scalar(
            select(TestCaseTable.id).where(
                TestCaseTable.story_id == story_id,
                TestCaseTable.number == int(code_match.group(1)),
            )
        )
        return test_case_id

    async def list_criterion_texts(self, criterion_ids: frozenset[UUID]) -> Mapping[UUID, str]:
        if not criterion_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(AcceptanceCriterionTable.id, AcceptanceCriterionTable.text).where(
                AcceptanceCriterionTable.id.in_(criterion_ids)
            )
        )
        return dict(result.all())

    async def list_cases(self, test_case_ids: frozenset[UUID]) -> Mapping[UUID, GapCase]:
        if not test_case_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(
                TestCaseTable.id,
                TestCaseTable.number,
                TestCaseTable.title,
                TestCaseVersionTable.number,
                TestCaseVersionTable.title,
                TestCaseVersionTable.preconditions,
                TestCaseVersionTable.steps,
            )
            .outerjoin(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .where(TestCaseTable.id.in_(test_case_ids))
        )
        return {
            case_id: GapCase(
                id=case_id,
                code=f"{TEST_CASE_CODE_PREFIX}{number}",
                title=version_title or title,
                version_number=version_number,
                preconditions=preconditions,
                steps=[] if steps is None else STEPS_ADAPTER.validate_python(steps),
            )
            for case_id, number, title, version_number, version_title, preconditions, steps in result
        }
