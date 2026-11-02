from typing import Annotated

from pydantic import StringConstraints

from app.modules.labels.typing.constants import MAX_LABEL_NAME_LENGTH
from app.modules.labels.typing.enums import LabelColor
from app.shared.common import WireModel


class UpdateLabelRequest(WireModel):
    name: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_LABEL_NAME_LENGTH)] | None
    ) = None
    color: LabelColor | None = None
