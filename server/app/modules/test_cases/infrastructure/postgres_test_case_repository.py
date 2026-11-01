from uuid import UUID

from sqlalchemy import ColumnElement, delete, exists, func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.domains.linked_test_case.entity import LinkedTestCase
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.modules.test_cases.domains.test_case_filter.entity import TestCaseFilter
from app.modules.test_cases.domains.test_case_summary.entity import TestCaseSummary
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.infrastructure.test_case_criterion_table import TestCaseCriterionTable
from app.modules.test_cases.infrastructure.test_case_table import TestCaseTable
from app.modules.test_cases.infrastructure.test_case_version_table import TestCaseVersionTable
from app.modules.test_cases.typing.enums import TestCaseStatus
from app.modules.test_cases.utils.case_code import find_case_number
from app.shared.postgres import Database


class PostgresTestCaseRepository(TestCaseRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_number(self, project_id: UUID, number: int) -> TestCase | None:
        row = await self._database.get_current_session().scalar(
            select(TestCaseTable)
            .where(TestCaseTable.project_id == project_id, TestCaseTable.number == number)
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestCase.model_validate(row)

    async def find_by_number_for_update(self, project_id: UUID, number: int) -> TestCase | None:
        row = await self._database.get_current_session().scalar(
            select(TestCaseTable)
            .where(TestCaseTable.project_id == project_id, TestCaseTable.number == number)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestCase.model_validate(row)

    async def list_summaries(self, project_id: UUID, case_filter: TestCaseFilter) -> list[TestCaseSummary]:
        statement = (
            select(
                TestCaseTable,
                StoryTable.jira_key,
                TestCaseVersionTable.number,
                func.jsonb_array_length(TestCaseVersionTable.steps),
                TestCaseVersionTable.criterion_ids,
                TestCaseVersionTable.created_at,
            )
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .where(TestCaseTable.project_id == project_id, *self._build_conditions(case_filter))
            .order_by(TestCaseTable.number)
            .execution_options(populate_existing=True)
        )
        result = await self._database.get_current_session().execute(statement)
        return [
            TestCaseSummary(
                test_case=TestCase.model_validate(row),
                story_key=story_key,
                current_version_number=version_number,
                step_count=step_count,
                criterion_ids=criterion_ids,
                last_saved_at=last_saved_at,
            )
            for row, story_key, version_number, step_count, criterion_ids, last_saved_at in result
        ]

    async def list_titles_for_stories(self, project_id: UUID, story_ids: frozenset[UUID]) -> set[tuple[UUID, str]]:
        result = await self._database.get_current_session().execute(
            select(TestCaseTable.story_id, TestCaseTable.title).where(
                TestCaseTable.project_id == project_id, TestCaseTable.story_id.in_(sorted(story_ids))
            )
        )
        return {(story_id, title.lower()) for story_id, title in result}

    async def list_linked_to_criteria_for_update(
        self, project_id: UUID, criterion_ids: frozenset[UUID]
    ) -> list[LinkedTestCase]:
        linked_ids = select(TestCaseCriterionTable.test_case_id).where(
            TestCaseCriterionTable.criterion_id.in_(sorted(criterion_ids))
        )
        session = self._database.get_current_session()
        rows = await session.scalars(
            select(TestCaseTable)
            .where(
                TestCaseTable.project_id == project_id,
                TestCaseTable.status != TestCaseStatus.DEPRECATED,
                TestCaseTable.id.in_(linked_ids),
            )
            .order_by(TestCaseTable.number)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        test_cases = [TestCase.model_validate(row) for row in rows]
        links = await session.execute(
            select(TestCaseCriterionTable.test_case_id, TestCaseCriterionTable.criterion_id).where(
                TestCaseCriterionTable.test_case_id.in_([test_case.id for test_case in test_cases]),
                TestCaseCriterionTable.criterion_id.in_(sorted(criterion_ids)),
            )
        )
        linked_criterion_ids: dict[UUID, set[UUID]] = {}
        for test_case_id, criterion_id in links:
            linked_criterion_ids.setdefault(test_case_id, set()).add(criterion_id)
        return [
            LinkedTestCase(
                test_case=test_case, linked_criterion_ids=frozenset(linked_criterion_ids.get(test_case.id, set()))
            )
            for test_case in test_cases
        ]

    async def create(self, test_case: TestCase, version: TestCaseVersion) -> None:
        session = self._database.get_current_session()
        await session.execute(insert(TestCaseTable).values({**test_case.model_dump(), "current_version_id": None}))
        await self.add_version(test_case, version)

    async def add_version(self, test_case: TestCase, version: TestCaseVersion) -> None:
        session = self._database.get_current_session()
        await session.execute(insert(TestCaseVersionTable).values(**version.model_dump()))
        await session.execute(
            update(TestCaseTable)
            .where(TestCaseTable.id == test_case.id)
            .values(title=version.title, priority=version.priority, current_version_id=version.id)
        )
        await session.execute(
            delete(TestCaseCriterionTable).where(
                TestCaseCriterionTable.test_case_id == test_case.id,
                TestCaseCriterionTable.criterion_id.not_in(version.criterion_ids),
            )
        )
        if version.criterion_ids:
            await session.execute(
                insert(TestCaseCriterionTable)
                .values(
                    [
                        {"test_case_id": test_case.id, "criterion_id": criterion_id, "created_at": version.created_at}
                        for criterion_id in version.criterion_ids
                    ]
                )
                .on_conflict_do_nothing()
            )

    async def save(self, test_case: TestCase) -> None:
        await self._database.get_current_session().execute(
            update(TestCaseTable)
            .where(TestCaseTable.id == test_case.id)
            .values(
                status=test_case.status,
                status_changed_at=test_case.status_changed_at,
                status_changed_by=test_case.status_changed_by,
                needs_review_at=test_case.needs_review_at,
                needs_review_criterion_ids=test_case.needs_review_criterion_ids,
                reviewed_at=test_case.reviewed_at,
                reviewed_by=test_case.reviewed_by,
            )
        )

    @staticmethod
    def _build_conditions(case_filter: TestCaseFilter) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if case_filter.story_key is not None:
            conditions.append(StoryTable.jira_key == case_filter.story_key)
        if case_filter.status is not None:
            conditions.append(TestCaseTable.status == case_filter.status)
        if case_filter.priority is not None:
            conditions.append(TestCaseTable.priority == case_filter.priority)
        if case_filter.criterion_id is not None:
            conditions.append(
                exists().where(
                    TestCaseCriterionTable.test_case_id == TestCaseTable.id,
                    TestCaseCriterionTable.criterion_id == case_filter.criterion_id,
                )
            )
        if case_filter.is_needing_review is not None:
            conditions.append(
                TestCaseTable.needs_review_at.is_not(None)
                if case_filter.is_needing_review
                else TestCaseTable.needs_review_at.is_(None)
            )
        if case_filter.query is not None:
            number = find_case_number(case_filter.query)
            conditions.append(
                TestCaseTable.title.icontains(case_filter.query, autoescape=True)
                if number is None
                else TestCaseTable.number == number
            )
        return conditions
