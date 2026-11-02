from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from app.modules.plans.typing.constants import MAX_PLAN_DESCRIPTION_LENGTH, MAX_PLAN_NAME_LENGTH
from app.shared.common import WireModel


class UpdatePlanRequest(WireModel):
    name: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_PLAN_NAME_LENGTH)] | None
    ) = None
    description: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_PLAN_DESCRIPTION_LENGTH)] | None
    ) = None
    target_date: date | None = None
    environment_id: UUID | None = None
