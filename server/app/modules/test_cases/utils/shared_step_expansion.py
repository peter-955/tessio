from collections.abc import Mapping, Sequence

from app.modules.shared_steps import CurrentSharedStep, UnknownSharedStepError
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_step.entity import TestStep


def expand_steps(steps: Sequence[TestStep], shared_steps: Mapping[str, CurrentSharedStep]) -> list[TestStep]:
    expanded: list[TestStep] = []
    for step in sorted(steps, key=lambda case_step: case_step.order):
        if not step.is_shared_step_reference or step.shared_step_key is None:
            expanded.append(step.model_copy(update={"order": len(expanded) + 1}))
            continue
        current = shared_steps.get(step.shared_step_key)
        if current is None:
            raise UnknownSharedStepError([step.shared_step_key])
        first_order = len(expanded)
        expanded.extend(
            TestStep(
                order=first_order + position,
                action=action.action,
                expected=action.expected,
                shared_step_key=step.shared_step_key,
                shared_step_version_number=current.version.number,
            )
            for position, action in enumerate(current.version.steps, start=1)
        )
    return expanded


def collect_shared_data_keys(keys: Sequence[str], shared_steps: Mapping[str, CurrentSharedStep]) -> frozenset[str]:
    return frozenset(
        data_key for key in keys if key in shared_steps for data_key in shared_steps[key].version.data_keys
    )


def expand_version(version: TestCaseVersion, shared_steps: Mapping[str, CurrentSharedStep]) -> TestCaseVersion:
    keys = version.shared_step_keys
    if not keys:
        return version
    data_keys = set(version.data_keys) | collect_shared_data_keys(keys, shared_steps)
    return version.model_copy(
        update={"steps": expand_steps(version.steps, shared_steps), "data_keys": sorted(data_keys)}
    )
