from uuid import UUID

from sqlalchemy import select

from app.modules.projects.infrastructure import ProjectTable
from app.modules.test_cases.ports.review_policy_reader import ReviewPolicyReader
from app.shared.postgres import Database


class PostgresReviewPolicyReader(ReviewPolicyReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_requiring_separate_reviewer(self, project_id: UUID) -> bool:
        is_requiring = await self._database.get_current_session().scalar(
            select(ProjectTable.require_separate_reviewer).where(ProjectTable.id == project_id)
        )
        return bool(is_requiring)
