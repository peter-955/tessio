from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.modules.test_cases.typing.constants import MAX_IMPORTED_CASES
from app.shared.common import WireModel


class CaseImportCommitRequest(WireModel):
    file_id: UUID
    indexes: list[Annotated[int, Field(ge=0)]] = Field(min_length=1, max_length=MAX_IMPORTED_CASES)
