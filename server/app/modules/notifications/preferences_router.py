from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.notifications.dependencies import (
    get_list_notification_preferences,
    get_update_notification_preferences,
)
from app.modules.notifications.models.notification_preference_response import NotificationPreferenceResponse
from app.modules.notifications.models.update_notification_preferences_request import (
    UpdateNotificationPreferencesRequest,
)
from app.modules.notifications.usecases.list_notification_preferences import ListNotificationPreferencesUseCase
from app.modules.notifications.usecases.update_notification_preferences import UpdateNotificationPreferencesUseCase
from app.modules.notifications.utils.notification_preference_response import (
    build_notification_preference_response,
    build_notification_setting_change,
)
from app.modules.projects import get_signed_in_actor
from app.shared.permissions import Actor

notification_preferences_router = APIRouter(
    prefix="/api/me/notification-preferences", tags=["notification-preferences"]
)

SignedInActor = Annotated[Actor, Depends(get_signed_in_actor)]


@notification_preferences_router.get("")
async def list_notification_preferences(
    actor: SignedInActor,
    use_case: Annotated[ListNotificationPreferencesUseCase, Depends(get_list_notification_preferences)],
) -> list[NotificationPreferenceResponse]:
    return [build_notification_preference_response(setting) for setting in await use_case.execute(actor)]


@notification_preferences_router.patch("")
async def update_notification_preferences(
    body: UpdateNotificationPreferencesRequest,
    actor: SignedInActor,
    use_case: Annotated[UpdateNotificationPreferencesUseCase, Depends(get_update_notification_preferences)],
) -> list[NotificationPreferenceResponse]:
    settings = await use_case.execute(actor, [build_notification_setting_change(change) for change in body.preferences])
    return [build_notification_preference_response(setting) for setting in settings]
