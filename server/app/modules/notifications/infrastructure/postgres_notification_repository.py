from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import aliased

from app.modules.notifications.domains.notification.entity import Notification
from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.modules.notifications.domains.notification_list_item.entity import NotificationListItem
from app.modules.notifications.infrastructure.notification_table import NotificationTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresNotificationRepository(NotificationRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add_all(self, notifications: Sequence[Notification]) -> None:
        self._database.get_current_session().add_all(
            [
                NotificationTable(
                    id=notification.id,
                    user_id=notification.user_id,
                    project_id=notification.project_id,
                    actor_id=notification.actor_id,
                    kind=notification.kind,
                    payload=notification.payload.model_dump(mode="json"),
                    read_at=notification.read_at,
                    created_at=notification.created_at,
                )
                for notification in notifications
            ]
        )

    async def list_for_user(
        self,
        user_id: UUID,
        project_ids: frozenset[UUID],
        is_unread_only: bool,
        cursor: UUID | None,
        limit: int,
    ) -> list[NotificationListItem]:
        if not project_ids:
            return []
        actor_table = aliased(UserTable)
        statement = (
            select(NotificationTable, ProjectTable.key, ProjectTable.name, actor_table.name)
            .join(ProjectTable, ProjectTable.id == NotificationTable.project_id)
            .outerjoin(actor_table, actor_table.id == NotificationTable.actor_id)
            .where(NotificationTable.user_id == user_id, NotificationTable.project_id.in_(project_ids))
            .order_by(NotificationTable.id.desc())
            .limit(limit)
        )
        if is_unread_only:
            statement = statement.where(NotificationTable.read_at.is_(None))
        if cursor is not None:
            statement = statement.where(NotificationTable.id < cursor)
        result = await self._database.get_current_session().execute(statement)
        return [
            NotificationListItem(
                notification=Notification.model_validate(row),
                project_key=project_key,
                project_name=project_name,
                actor_name=actor_name,
            )
            for row, project_key, project_name, actor_name in result
        ]

    async def count_unread(self, user_id: UUID, project_ids: frozenset[UUID]) -> int:
        if not project_ids:
            return 0
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(NotificationTable)
            .where(
                NotificationTable.user_id == user_id,
                NotificationTable.project_id.in_(project_ids),
                NotificationTable.read_at.is_(None),
            )
        )
        return count or 0

    async def find_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        row = await self._database.get_current_session().scalar(
            select(NotificationTable).where(
                NotificationTable.id == notification_id, NotificationTable.user_id == user_id
            )
        )
        return None if row is None else Notification.model_validate(row)

    async def mark_read(self, notification_id: UUID, now: datetime) -> None:
        await self._database.get_current_session().execute(
            update(NotificationTable)
            .where(NotificationTable.id == notification_id, NotificationTable.read_at.is_(None))
            .values(read_at=now)
        )

    async def mark_all_read(self, user_id: UUID, now: datetime) -> int:
        marked_ids = await self._database.get_current_session().scalars(
            update(NotificationTable)
            .where(NotificationTable.user_id == user_id, NotificationTable.read_at.is_(None))
            .values(read_at=now)
            .returning(NotificationTable.id)
        )
        return len(marked_ids.all())
