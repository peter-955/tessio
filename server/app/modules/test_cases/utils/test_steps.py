from collections.abc import Sequence

from app.modules.shared_steps import InvalidStepShapeError, normalize_shared_step_key
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.models.test_step_request import TestStepRequest


def build_test_steps(requests: Sequence[TestStepRequest]) -> list[TestStep]:
    steps: list[TestStep] = []
    for order, request in enumerate(requests, start=1):
        if request.shared_step_key is not None:
            if request.action or request.expected:
                raise InvalidStepShapeError(f"Step {order}: a shared step has no action or expected result of its own.")
            steps.append(TestStep(order=order, shared_step_key=normalize_shared_step_key(request.shared_step_key)))
            continue
        if not request.action:
            raise InvalidStepShapeError(f"Step {order}: write the action, or pick a shared step.")
        steps.append(TestStep(order=order, action=request.action, expected=request.expected))
    return steps
