from pydantic import BaseModel, ConfigDict, field_validator

from app.shared.common.nul_character import contains_nul_character
from app.shared.typing.constants import NUL_CHARACTER_MESSAGE


class ToolModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    @field_validator("*", mode="after")
    @classmethod
    def reject_nul_characters[FieldValue](cls, value: FieldValue) -> FieldValue:
        if contains_nul_character(value):
            raise ValueError(NUL_CHARACTER_MESSAGE)
        return value
