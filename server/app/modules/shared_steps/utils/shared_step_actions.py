import re
from collections.abc import Iterable, Sequence

from app.modules.shared_steps.domains.shared_step_action.entity import SharedStepAction
from app.modules.shared_steps.errors import InvalidStepShapeError
from app.modules.shared_steps.models.shared_step_action_request import SharedStepActionRequest
from app.modules.shared_steps.typing.constants import DATA_REFERENCE_PATTERN


def build_shared_step_actions(requests: Sequence[SharedStepActionRequest]) -> list[SharedStepAction]:
    actions: list[SharedStepAction] = []
    for order, request in enumerate(requests, start=1):
        if request.shared_step_key is not None:
            raise InvalidStepShapeError(f"Step {order}: a shared step cannot contain another shared step.")
        if not request.action:
            raise InvalidStepShapeError(f"Step {order}: write the action.")
        actions.append(SharedStepAction(order=order, action=request.action, expected=request.expected or None))
    return actions


def collect_data_keys(texts: Iterable[str | None]) -> list[str]:
    keys = {key for text in texts if text for key in re.findall(DATA_REFERENCE_PATTERN, text)}
    return sorted(keys)


def collect_action_data_keys(actions: Sequence[SharedStepAction]) -> list[str]:
    return collect_data_keys(text for action in actions for text in (action.action, action.expected))
