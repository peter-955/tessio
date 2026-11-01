from uuid import UUID

from sqlalchemy import ColumnElement, or_, select

from app.modules.notifications.ports.recipient_directory import RecipientDirectory
from app.modules.projects.infrastructure import ProjectMemberTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.permissions import ProjectRole
from app.shared.postgres import Database


class PostgresRecipientDirectory(RecipientDirectory):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_active_recipient_ids(
        self, project_id: UUID, user_ids: frozenset[UUID], roles: frozenset[ProjectRole]
    ) -> frozenset[UUID]:
        recipient_conditions: list[ColumnElement[bool]] = []
        if user_ids:
            recipient_conditions.append(UserTable.id.in_(user_ids))
        if roles:
            member_user_ids = select(ProjectMemberTable.user_id).where(
                ProjectMemberTable.project_id == project_id, ProjectMemberTable.role.in_(roles)
            )
            recipient_conditions.append(UserTable.id.in_(member_user_ids))
        if not recipient_conditions:
            return frozenset()
        recipient_ids = await self._database.get_current_session().scalars(
            select(UserTable.id).where(UserTable.status == UserStatus.ACTIVE, or_(*recipient_conditions))
        )
        return frozenset(recipient_ids)
