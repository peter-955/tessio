from uuid import UUID

from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.modules.notifications.domains.notification_page.entity import NotificationPage
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectAccessResolver


class ListNotificationsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        notification_repository: NotificationRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._notification_repository = notification_repository

    async def execute(self, actor: Actor, is_unread_only: bool, cursor: UUID | None, limit: int) -> NotificationPage:
        async with self._transaction.begin():
            project_ids = await self._project_access_resolver.list_visible_project_ids(actor)
            items = await self._notification_repository.list_for_user(
                actor.user_id, project_ids, is_unread_only, cursor, limit + 1
            )
        has_more = len(items) > limit
        page_items = items[:limit]
        next_cursor = page_items[-1].notification.id if has_more else None
        return NotificationPage(items=page_items, next_cursor=next_cursor)
