from collections.abc import Sequence
from uuid import UUID

from app.modules.shared_steps import SharedStepRepository
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.utils.shared_step_expansion import expand_version


class CaseStepExpander:
    def __init__(self, shared_step_repository: SharedStepRepository) -> None:
        self._shared_step_repository = shared_step_repository

    async def expand(self, project_id: UUID, versions: Sequence[TestCaseVersion]) -> list[TestCaseVersion]:
        keys = {key for version in versions for key in version.shared_step_keys}
        if not keys:
            return list(versions)
        current_steps = await self._shared_step_repository.list_current_by_keys(project_id, keys)
        shared_steps = {current.shared_step.key: current for current in current_steps}
        return [expand_version(version, shared_steps) for version in versions]
