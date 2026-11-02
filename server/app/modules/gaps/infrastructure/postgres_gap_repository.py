from collections.abc import Mapping, Sequence
from uuid import UUID

from sqlalchemy import Row, Select, and_, case, func, literal, or_, select
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy.orm import aliased

from app.modules.gaps.domains.gap.entity import Gap
from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.domains.similar_answer.entity import SimilarAnswer
from app.modules.gaps.infrastructure.gap_table import GapTable
from app.modules.gaps.typing.constants import SEARCH_CONFIGURATION, SEARCH_TERM_SEPARATOR, TEST_CASE_CODE_PREFIX
from app.modules.gaps.typing.enums import GapStatus, GapTargetType
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresGapRepository(GapRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_for_update(self, project_id: UUID, gap_id: UUID) -> Gap | None:
        row = await self._database.get_current_session().scalar(
            select(GapTable)
            .where(GapTable.project_id == project_id, GapTable.id == gap_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Gap.model_validate(row)

    async def add_all(self, gaps: list[Gap]) -> None:
        self._database.get_current_session().add_all([GapTable(**gap.model_dump()) for gap in gaps])

    async def save(self, gap: Gap) -> None:
        await self._database.get_current_session().merge(GapTable(**gap.model_dump()))

    async def count_open(self, story_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(GapTable)
            .where(GapTable.story_id == story_id, GapTable.status == GapStatus.OPEN)
        )
        return count or 0

    async def count_open_by_story(self, story_ids: frozenset[UUID]) -> Mapping[UUID, int]:
        counts = dict.fromkeys(story_ids, 0)
        if not story_ids:
            return counts
        result = await self._database.get_current_session().execute(
            select(GapTable.story_id, func.count())
            .where(GapTable.story_id.in_(story_ids), GapTable.status == GapStatus.OPEN)
            .group_by(GapTable.story_id)
        )
        for story_id, count in result:
            counts[story_id] = count
        return counts

    async def list_similar_answers(
        self, project_id: UUID, story_id: UUID, terms: Sequence[str], limit: int
    ) -> list[SimilarAnswer]:
        if not terms:
            return []
        query = func.websearch_to_tsquery(
            literal(SEARCH_CONFIGURATION).cast(REGCONFIG), SEARCH_TERM_SEPARATOR.join(terms)
        )
        result = await self._database.get_current_session().execute(
            select(GapTable.story_id, StoryTable.jira_key, GapTable.question, GapTable.answer)
            .join(StoryTable, StoryTable.id == GapTable.story_id)
            .where(
                GapTable.project_id == project_id,
                GapTable.status == GapStatus.RESOLVED,
                GapTable.answer.is_not(None),
                GapTable.search_vector.bool_op("@@")(query),
            )
            .order_by(
                (GapTable.story_id == story_id).desc(),
                func.ts_rank(GapTable.search_vector, query).desc(),
                GapTable.answered_at.desc().nulls_last(),
                GapTable.id,
            )
            .limit(limit)
        )
        return [
            SimilarAnswer(story_id=row_story_id, story_jira_key=jira_key, question=question, answer=answer)
            for row_story_id, jira_key, question, answer in result
        ]

    async def find_view(self, project_id: UUID, gap_id: UUID) -> GapView | None:
        result = await self._database.get_current_session().execute(
            self._select_views().where(GapTable.project_id == project_id, GapTable.id == gap_id)
        )
        row = result.one_or_none()
        return None if row is None else self._build_view(row)

    async def list_views(self, project_id: UUID, gap_filter: GapFilter) -> list[GapView]:
        statement = self._select_views().where(GapTable.project_id == project_id)
        if gap_filter.story_id is not None:
            statement = statement.where(GapTable.story_id == gap_filter.story_id)
        if gap_filter.status is not None:
            statement = statement.where(GapTable.status == gap_filter.status)
        if gap_filter.assigned_to is not None:
            recipient = gap_filter.assigned_to
            if recipient.role is None:
                statement = statement.where(GapTable.assignee_id == recipient.user_id)
            else:
                statement = statement.where(
                    or_(
                        GapTable.assignee_id == recipient.user_id,
                        and_(GapTable.assignee_id.is_(None), GapTable.assignee_role == recipient.role),
                    )
                )
        result = await self._database.get_current_session().execute(statement)
        return [self._build_view(row) for row in result]

    async def list_inbox_views(
        self, user_id: UUID, project_ids: frozenset[UUID], is_including_resolved: bool, limit: int
    ) -> list[GapView]:
        if not project_ids:
            return []
        statement = (
            self._select_views()
            .outerjoin(
                ProjectMemberTable,
                and_(ProjectMemberTable.project_id == GapTable.project_id, ProjectMemberTable.user_id == user_id),
            )
            .where(
                GapTable.project_id.in_(project_ids),
                ProjectTable.archived_at.is_(None),
                or_(
                    GapTable.assignee_id == user_id,
                    and_(GapTable.assignee_id.is_(None), GapTable.assignee_role == ProjectMemberTable.role),
                ),
            )
            .limit(limit)
        )
        if not is_including_resolved:
            statement = statement.where(GapTable.status == GapStatus.OPEN)
        result = await self._database.get_current_session().execute(statement)
        return [self._build_view(row) for row in result]

    @staticmethod
    def _select_views() -> Select[
        GapTable, str, str, str, str, str | None, str | None, UserStatus | None, str, str | None, str | None
    ]:
        assignee = aliased(UserTable)
        raiser = aliased(UserTable)
        answerer = aliased(UserTable)
        reopener = aliased(UserTable)
        target_ref = case(
            (GapTable.target_type == GapTargetType.CRITERION, AcceptanceCriterionTable.code),
            (
                GapTable.target_type == GapTargetType.TEST_CASE,
                func.concat(TEST_CASE_CODE_PREFIX, TestCaseTable.number),
            ),
            else_=None,
        )
        return (
            select(
                GapTable,
                ProjectTable.key,
                ProjectTable.name,
                StoryTable.jira_key,
                StoryTable.title,
                target_ref,
                assignee.name,
                assignee.status,
                raiser.name,
                answerer.name,
                reopener.name,
            )
            .join(ProjectTable, ProjectTable.id == GapTable.project_id)
            .join(StoryTable, StoryTable.id == GapTable.story_id)
            .join(raiser, raiser.id == GapTable.raised_by)
            .outerjoin(
                AcceptanceCriterionTable,
                and_(
                    GapTable.target_type == GapTargetType.CRITERION,
                    AcceptanceCriterionTable.id == GapTable.target_id,
                ),
            )
            .outerjoin(
                TestCaseTable,
                and_(GapTable.target_type == GapTargetType.TEST_CASE, TestCaseTable.id == GapTable.target_id),
            )
            .outerjoin(assignee, assignee.id == GapTable.assignee_id)
            .outerjoin(answerer, answerer.id == GapTable.answered_by)
            .outerjoin(reopener, reopener.id == GapTable.reopened_by)
            .order_by(GapTable.created_at.desc(), GapTable.id.desc())
        )

    @staticmethod
    def _build_view(
        row: Row[GapTable, str, str, str, str, str | None, str | None, UserStatus | None, str, str | None, str | None],
    ) -> GapView:
        (
            gap_row,
            project_key,
            project_name,
            story_jira_key,
            story_title,
            target_ref,
            assignee_name,
            assignee_status,
            raised_by_name,
            answered_by_name,
            reopened_by_name,
        ) = row
        return GapView(
            gap=Gap.model_validate(gap_row),
            project_key=project_key,
            project_name=project_name,
            story_jira_key=story_jira_key,
            story_title=story_title,
            target_ref=target_ref,
            assignee_name=assignee_name,
            assignee_status=assignee_status,
            raised_by_name=raised_by_name,
            answered_by_name=answered_by_name,
            reopened_by_name=reopened_by_name,
        )
