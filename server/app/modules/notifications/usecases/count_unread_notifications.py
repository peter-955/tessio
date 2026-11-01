from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectAccessResolver


class CountUnreadNotificationsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        notification_repository: NotificationRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._notification_repository = notification_repository

    async def execute(self, actor: Actor) -> int:
        async with self._transaction.begin():
            project_ids = await self._project_access_resolver.list_visible_project_ids(actor)
            return await self._notification_repository.count_unread(actor.user_id, project_ids)
