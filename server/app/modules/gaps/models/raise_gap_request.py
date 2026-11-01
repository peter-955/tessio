from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from app.modules.gaps.typing.constants import MAX_QUESTION_LENGTH, MAX_TARGET_REF_LENGTH
from app.modules.gaps.typing.enums import GapDataScope, GapSeverity, GapTargetType, GapType
from app.shared.common import WireModel


class RaiseGapRequest(WireModel):
    type: GapType
    severity: GapSeverity = GapSeverity.MEDIUM
    target_type: GapTargetType = GapTargetType.STORY
    target_ref: Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_TARGET_REF_LENGTH)] | None = None
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_QUESTION_LENGTH)]
    data_scope: GapDataScope | None = None
    assignee_id: UUID | None = None
