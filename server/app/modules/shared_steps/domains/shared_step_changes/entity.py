from app.modules.shared_steps.domains.shared_step_action.entity import SharedStepAction
from app.shared.common import Entity


class SharedStepChanges(Entity):
    title: str | None = None
    steps: list[SharedStepAction] | None = None
    is_archived: bool | None = None
