import re
from uuid import UUID

from sqlalchemy import select

from app.modules.gaps.domains.gap_story.entity import GapStory
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.constants import TEST_CASE_CODE_PATTERN
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.shared.postgres import Database


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
