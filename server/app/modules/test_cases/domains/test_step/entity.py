from typing import Any

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer

from app.modules.test_cases.typing.constants.test_case import SHARED_STEP_FIELDS
from app.shared.common import Entity


class TestStep(Entity):
    order: int = Field(ge=1)
    action: str | None = None
    expected: str | None = None
    shared_step_key: str | None = None
    shared_step_version_number: int | None = None

    @property
    def is_shared_step_reference(self) -> bool:
        return self.action is None and self.shared_step_key is not None

    @model_serializer(mode="wrap")
    def drop_empty_shared_step_fields(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        dumped: dict[str, Any] = handler(self)
        for field_name in SHARED_STEP_FIELDS:
            if dumped.get(field_name) is None:
                dumped.pop(field_name, None)
        if self.is_shared_step_reference:
            dumped.pop("action", None)
            dumped.pop("expected", None)
        return dumped
