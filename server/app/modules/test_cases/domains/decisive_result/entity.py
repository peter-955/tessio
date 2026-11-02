from datetime import datetime
from uuid import UUID

from app.modules.test_cases.typing.enums import ResultExecutorKind
from app.shared.common import Entity


class DecisiveResult(Entity):
    case_result_id: UUID
    test_case_version_id: UUID
    is_passed: bool
    executor_kind: ResultExecutorKind
    recorded_at: datetime
