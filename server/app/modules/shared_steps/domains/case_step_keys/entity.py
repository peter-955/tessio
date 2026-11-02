from app.shared.common import Entity


class CaseStepKeys(Entity):
    code: str
    step_keys: list[str | None]
