from typing import Annotated

from pydantic import StringConstraints

from app.modules.test_data.typing.constants import (
    ENVIRONMENT_URL_PATTERN,
    MAX_ENVIRONMENT_NAME_LENGTH,
    MAX_ENVIRONMENT_URL_LENGTH,
)
from app.shared.common import WireModel

EnvironmentUrl = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=ENVIRONMENT_URL_PATTERN, max_length=MAX_ENVIRONMENT_URL_LENGTH),
]


class EnvironmentRequest(WireModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_ENVIRONMENT_NAME_LENGTH)]
    base_url: EnvironmentUrl
    health_check_url: EnvironmentUrl | None = None
