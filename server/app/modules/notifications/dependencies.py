from fastapi import Request

from app.modules.notifications.usecases.count_unread_notifications import CountUnreadNotificationsUseCase
from app.modules.notifications.usecases.list_notifications import ListNotificationsUseCase
from app.modules.notifications.usecases.mark_all_notifications_read import MarkAllNotificationsReadUseCase
from app.modules.notifications.usecases.mark_notification_read import MarkNotificationReadUseCase


def get_list_notifications(request: Request) -> ListNotificationsUseCase:
    use_case: ListNotificationsUseCase = request.app.state.container.list_notifications
    return use_case


def get_count_unread_notifications(request: Request) -> CountUnreadNotificationsUseCase:
    use_case: CountUnreadNotificationsUseCase = request.app.state.container.count_unread_notifications
    return use_case


def get_mark_notification_read(request: Request) -> MarkNotificationReadUseCase:
    use_case: MarkNotificationReadUseCase = request.app.state.container.mark_notification_read
    return use_case


def get_mark_all_notifications_read(request: Request) -> MarkAllNotificationsReadUseCase:
    use_case: MarkAllNotificationsReadUseCase = request.app.state.container.mark_all_notifications_read
    return use_case
