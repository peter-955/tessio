from uuid import UUID

from app.modules.shared_steps import SharedStepRepository
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.utils.case_content_rules import (
    require_data_table,
    require_expanded_step_limit,
    require_known_shared_steps,
    require_no_secret_values,
)
from app.modules.test_cases.utils.shared_step_expansion import collect_shared_data_keys
from app.modules.test_data import SecretValueReader


async def check_case_content(
    shared_step_repository: SharedStepRepository,
    secret_value_reader: SecretValueReader,
    project_id: UUID,
    content: TestCaseContent,
    previous_version: TestCaseVersion | None,
) -> frozenset[str]:
    require_data_table(content.parameters, content.data_rows)
    keys = list(dict.fromkeys(step.shared_step_key for step in content.steps if step.is_shared_step_reference))
    shared_keys = [key for key in keys if key is not None]
    current_steps = await shared_step_repository.list_current_by_keys(project_id, shared_keys)
    shared_steps = {current.shared_step.key: current for current in current_steps}
    kept_keys = frozenset() if previous_version is None else frozenset(previous_version.shared_step_keys)
    require_known_shared_steps(content.steps, shared_steps, kept_keys)
    require_expanded_step_limit(content.steps, shared_steps)
    is_new_rows = previous_version is None or content.data_rows != previous_version.data_rows
    if content.data_rows and is_new_rows:
        require_no_secret_values(content.data_rows, await secret_value_reader.list_project_secret_values(project_id))
    return collect_shared_data_keys(shared_keys, shared_steps)
