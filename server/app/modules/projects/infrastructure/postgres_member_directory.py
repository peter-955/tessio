from uuid import UUID

from sqlalchemy import or_, select

from app.modules.projects.domains.candidate_user.entity import CandidateUser
from app.modules.projects.domains.member_profile.entity import MemberProfile
from app.modules.projects.infrastructure.project_member_table import ProjectMemberTable
from app.modules.projects.ports.member_directory import MemberDirectory
from app.modules.projects.typing.constants.search import LIKE_ESCAPE_CHARACTER
from app.modules.projects.utils.like_pattern import build_contains_pattern
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresMemberDirectory(MemberDirectory):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_member_profiles(self, project_id: UUID) -> list[MemberProfile]:
        result = await self._database.get_current_session().execute(
            select(
                UserTable.id,
                UserTable.name,
                UserTable.email,
                UserTable.status,
                ProjectMemberTable.role,
                ProjectMemberTable.created_at,
            )
            .join(ProjectMemberTable, ProjectMemberTable.user_id == UserTable.id)
            .where(ProjectMemberTable.project_id == project_id)
            .order_by(UserTable.name, UserTable.email)
        )
        return [
            MemberProfile(user_id=user_id, name=name, email=email, user_status=status, role=role, created_at=created_at)
            for user_id, name, email, status, role, created_at in result
        ]

    async def list_candidates(self, project_id: UUID, query: str | None, limit: int) -> list[CandidateUser]:
        member_user_ids = select(ProjectMemberTable.user_id).where(ProjectMemberTable.project_id == project_id)
        statement = (
            select(UserTable.id, UserTable.name, UserTable.email, UserTable.status)
            .where(
                UserTable.status.in_([UserStatus.ACTIVE, UserStatus.INVITED]),
                UserTable.id.not_in(member_user_ids),
            )
            .order_by(UserTable.name, UserTable.email)
            .limit(limit)
        )
        if query is not None:
            pattern = build_contains_pattern(query)
            statement = statement.where(
                or_(
                    UserTable.name.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                    UserTable.email.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                )
            )
        result = await self._database.get_current_session().execute(statement)
        return [
            CandidateUser(user_id=user_id, name=name, email=email, user_status=status)
            for user_id, name, email, status in result
        ]
