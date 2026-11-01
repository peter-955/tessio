from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

from app.shared.common.nul_character import contains_nul_character
from app.shared.typing.constants import NUL_CHARACTER_MESSAGE


class WireModel(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    @field_validator("*", mode="after")
    @classmethod
    def reject_nul_characters[FieldValue](cls, value: FieldValue) -> FieldValue:
        if contains_nul_character(value):
            raise ValueError(NUL_CHARACTER_MESSAGE)
        return value
