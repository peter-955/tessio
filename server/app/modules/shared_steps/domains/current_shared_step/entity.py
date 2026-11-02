from app.modules.shared_steps.domains.shared_step.entity import SharedStep
from app.modules.shared_steps.domains.shared_step_version.entity import SharedStepVersion
from app.shared.common import Entity


class CurrentSharedStep(Entity):
    shared_step: SharedStep
    version: SharedStepVersion
