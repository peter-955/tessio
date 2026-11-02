from uuid import UUID

from app.modules.runs.typing.enums import RunExecutor
from app.shared.common import Entity


class SuiteRunOpening(Entity):
    suite_id: UUID
    environment_id: UUID | None
    executor: RunExecutor
    parent_run_id: UUID | None
    test_case_ids: list[UUID] | None
