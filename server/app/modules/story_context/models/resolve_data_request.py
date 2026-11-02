from typing import Annotated

from pydantic import Field

from app.modules.story_context.typing.constants import MAX_DATA_KEY_LENGTH, MAX_RESOLVE_KEYS
from app.shared.common import WireModel


class ResolveDataRequest(WireModel):
    keys: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=MAX_DATA_KEY_LENGTH)]],
        Field(min_length=1, max_length=MAX_RESOLVE_KEYS),
    ]
