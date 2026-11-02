from uuid import UUID

from pydantic import Field

from app.modules.labels import MAX_LABELS_PER_CASE
from app.shared.common import WireModel


class SetTestCaseLabelsRequest(WireModel):
    label_ids: list[UUID] = Field(max_length=MAX_LABELS_PER_CASE)
