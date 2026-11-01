from collections.abc import Sequence

from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.models.test_step_request import TestStepRequest


def build_test_steps(requests: Sequence[TestStepRequest]) -> list[TestStep]:
    return [
        TestStep(order=order, action=request.action, expected=request.expected)
        for order, request in enumerate(requests, start=1)
    ]
