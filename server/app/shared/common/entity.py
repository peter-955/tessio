from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
