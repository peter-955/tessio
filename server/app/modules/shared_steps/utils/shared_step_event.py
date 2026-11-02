from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.shared.events import LiveEvent, LiveEventType


def build_shared_step_changed_event(shared_step: SharedStep) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.SHARED_STEP_CHANGED,
        project_id=shared_step.project_id,
        ids={"sharedStepKey": shared_step.key, "sharedStepId": str(shared_step.id)},
    )
