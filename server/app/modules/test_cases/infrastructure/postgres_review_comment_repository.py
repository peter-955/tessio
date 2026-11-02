from uuid import UUID

from sqlalchemy import ColumnElement, func, insert, select
from sqlalchemy.orm import aliased

from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView
from app.modules.test_cases.infrastructure.test_case_review_comment_table import TestCaseReviewCommentTable
from app.modules.test_cases.infrastructure.test_case_version_table import TestCaseVersionTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresReviewCommentRepository(ReviewCommentRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_for_update(self, test_case_id: UUID, comment_id: UUID) -> ReviewComment | None:
        row = await self._database.get_current_session().scalar(
            select(TestCaseReviewCommentTable)
            .where(
                TestCaseReviewCommentTable.test_case_id == test_case_id,
                TestCaseReviewCommentTable.id == comment_id,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else ReviewComment.model_validate(row)

    async def find_view(self, comment_id: UUID) -> ReviewCommentView | None:
        views = await self._list_views(TestCaseReviewCommentTable.id == comment_id)
        return views[0] if views else None

    async def list_views(self, test_case_id: UUID) -> list[ReviewCommentView]:
        return await self._list_views(TestCaseReviewCommentTable.test_case_id == test_case_id)

    async def count_open(self, test_case_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(TestCaseReviewCommentTable)
            .where(
                TestCaseReviewCommentTable.test_case_id == test_case_id,
                TestCaseReviewCommentTable.resolved_at.is_(None),
            )
        )
        return count or 0

    async def create(self, comment: ReviewComment) -> None:
        await self._database.get_current_session().execute(
            insert(TestCaseReviewCommentTable).values(comment.model_dump())
        )

    async def save(self, comment: ReviewComment) -> None:
        await self._database.get_current_session().merge(TestCaseReviewCommentTable(**comment.model_dump()))

    async def _list_views(self, *conditions: ColumnElement[bool]) -> list[ReviewCommentView]:
        author = aliased(UserTable)
        resolver = aliased(UserTable)
        result = await self._database.get_current_session().execute(
            select(TestCaseReviewCommentTable, TestCaseVersionTable.number, author.name, resolver.name)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseReviewCommentTable.version_id)
            .join(author, author.id == TestCaseReviewCommentTable.author_id)
            .outerjoin(resolver, resolver.id == TestCaseReviewCommentTable.resolved_by)
            .where(*conditions)
            .order_by(TestCaseReviewCommentTable.created_at, TestCaseReviewCommentTable.id)
            .execution_options(populate_existing=True)
        )
        return [
            ReviewCommentView(
                comment=ReviewComment.model_validate(row),
                version_number=version_number,
                author_name=author_name,
                resolved_by_name=resolved_by_name,
            )
            for row, version_number, author_name, resolved_by_name in result
        ]
