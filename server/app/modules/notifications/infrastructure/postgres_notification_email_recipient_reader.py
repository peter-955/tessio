from uuid import UUID

from sqlalchemy import select

from app.modules.notifications.domains.notification_email_recipient.entity import NotificationEmailRecipient
from app.modules.notifications.ports.notification_email_recipient_reader import NotificationEmailRecipientReader
from app.modules.projects.infrastructure import ProjectTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresNotificationEmailRecipientReader(NotificationEmailRecipientReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_active_recipient(self, user_id: UUID, project_id: UUID) -> NotificationEmailRecipient | None:
        row = (
            await self._database.get_current_session().execute(
                select(UserTable.email, UserTable.name, UserTable.language, ProjectTable.key, ProjectTable.name)
                .join(ProjectTable, ProjectTable.id == project_id)
                .where(UserTable.id == user_id, UserTable.status == UserStatus.ACTIVE)
            )
        ).first()
        if row is None:
            return None
        email, name, language, project_key, project_name = row
        return NotificationEmailRecipient(
            email=email, name=name, language=language, project_key=project_key, project_name=project_name
        )
