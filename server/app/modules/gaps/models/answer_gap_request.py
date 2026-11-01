from typing import Annotated

from pydantic import StringConstraints

from app.modules.gaps.typing.constants import MAX_ANSWER_LENGTH
from app.shared.common import WireModel


class AnswerGapRequest(WireModel):
    answer: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_ANSWER_LENGTH)]
