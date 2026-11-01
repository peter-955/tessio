from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.modules.notifications.models.failure_assigned_payload_response import FailureAssignedPayloadResponse
from app.modules.notifications.models.gap_assigned_payload_response import GapAssignedPayloadResponse
from app.modules.notifications.models.run_finished_payload_response import RunFinishedPayloadResponse
from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class NotificationResponse(WireModel):
    id: UUID
    kind: NotificationKind
    project_id: UUID
    project_key: str
    project_name: str
    actor_id: UUID | None
    actor_name: str | None
    payload: Annotated[
        GapAssignedPayloadResponse | FailureAssignedPayloadResponse | RunFinishedPayloadResponse,
        Field(discriminator="kind"),
    ]
    is_read: bool
    read_at: datetime | None
    created_at: datetime
