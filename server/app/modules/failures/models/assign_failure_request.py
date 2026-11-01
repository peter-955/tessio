from uuid import UUID

from app.shared.common import WireModel


class AssignFailureRequest(WireModel):
    assignee_id: UUID | None
