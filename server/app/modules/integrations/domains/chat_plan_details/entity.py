from datetime import date
from uuid import UUID

from app.shared.common import Entity


class ChatPlanDetails(Entity):
    id: UUID
    name: str
    signed_off_by_name: str | None
    target_date: date | None
