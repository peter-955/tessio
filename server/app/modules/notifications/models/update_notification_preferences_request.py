from typing import Annotated

from pydantic import Field

from app.modules.notifications.models.notification_preference_change_request import (
    NotificationPreferenceChangeRequest,
)
from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class UpdateNotificationPreferencesRequest(WireModel):
    preferences: Annotated[list[NotificationPreferenceChangeRequest], Field(max_length=len(NotificationKind))]
