from typing import Annotated

from pydantic import StringConstraints

from app.modules.suites.typing.constants.suite import MAX_SUITE_DESCRIPTION_LENGTH, MAX_SUITE_NAME_LENGTH
from app.shared.common import WireModel


class UpdateSuiteRequest(WireModel):
    name: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_SUITE_NAME_LENGTH)] | None
    ) = None
    description: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=MAX_SUITE_DESCRIPTION_LENGTH)] | None
    ) = None
