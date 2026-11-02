from fastapi import Request

from app.modules.notifications.usecases.count_unread_notifications import CountUnreadNotificationsUseCase
from app.modules.notifications.usecases.list_notification_preferences import ListNotificationPreferencesUseCase
from app.modules.notifications.usecases.list_notifications import ListNotificationsUseCase
from app.modules.notifications.usecases.mark_all_notifications_read import MarkAllNotificationsReadUseCase
from app.modules.notifications.usecases.mark_notification_read import MarkNotificationReadUseCase
from app.modules.notifications.usecases.update_notification_preferences import UpdateNotificationPreferencesUseCase


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


def get_list_notification_preferences(request: Request) -> ListNotificationPreferencesUseCase:
    use_case: ListNotificationPreferencesUseCase = request.app.state.container.list_notification_preferences
    return use_case


def get_update_notification_preferences(request: Request) -> UpdateNotificationPreferencesUseCase:
    use_case: UpdateNotificationPreferencesUseCase = request.app.state.container.update_notification_preferences
    return use_case
