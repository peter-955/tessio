from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.modules.notifications.dependencies import (
    get_count_unread_notifications,
    get_list_notifications,
    get_mark_all_notifications_read,
    get_mark_notification_read,
)
from app.modules.notifications.models.notification_page_response import NotificationPageResponse
from app.modules.notifications.models.unread_notification_count_response import UnreadNotificationCountResponse
from app.modules.notifications.typing.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.modules.notifications.usecases.count_unread_notifications import CountUnreadNotificationsUseCase
from app.modules.notifications.usecases.list_notifications import ListNotificationsUseCase
from app.modules.notifications.usecases.mark_all_notifications_read import MarkAllNotificationsReadUseCase
from app.modules.notifications.usecases.mark_notification_read import MarkNotificationReadUseCase
from app.modules.notifications.utils.notification_response import build_notification_response
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

notifications_router = APIRouter(prefix="/api/notifications", tags=["notifications"])

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@notifications_router.get("")
async def list_notifications(
    actor: SignedInActor,
    use_case: Annotated[ListNotificationsUseCase, Depends(get_list_notifications)],
    is_unread_only: Annotated[bool, Query(alias="unreadOnly")] = False,
    cursor: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> NotificationPageResponse:
    page = await use_case.execute(actor, is_unread_only, cursor, limit)
    return NotificationPageResponse(
        items=[build_notification_response(item) for item in page.items], next_cursor=page.next_cursor
    )


@notifications_router.get("/unread-count")
async def count_unread_notifications(
    actor: SignedInActor,
    use_case: Annotated[CountUnreadNotificationsUseCase, Depends(get_count_unread_notifications)],
) -> UnreadNotificationCountResponse:
    return UnreadNotificationCountResponse(count=await use_case.execute(actor))


@notifications_router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_notifications_read(
    actor: SignedInActor,
    use_case: Annotated[MarkAllNotificationsReadUseCase, Depends(get_mark_all_notifications_read)],
) -> None:
    await use_case.execute(actor)


@notifications_router.put("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID,
    actor: SignedInActor,
    use_case: Annotated[MarkNotificationReadUseCase, Depends(get_mark_notification_read)],
) -> None:
    await use_case.execute(actor, notification_id)
