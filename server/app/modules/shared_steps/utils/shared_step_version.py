from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid7

from app.modules.shared_steps.domains.shared_step_action.entity import SharedStepAction
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.modules.shared_steps.utils.shared_step_actions import collect_action_data_keys


def build_shared_step_version(
    shared_step_id: UUID, number: int, actions: Sequence[SharedStepAction], created_by: UUID, created_at: datetime
) -> SharedStepVersion:
    steps = [action.model_copy(update={"order": order}) for order, action in enumerate(actions, start=1)]
    return SharedStepVersion(
        id=uuid7(),
        shared_step_id=shared_step_id,
        number=number,
        steps=steps,
        data_keys=collect_action_data_keys(steps),
        created_by=created_by,
        created_at=created_at,
    )
