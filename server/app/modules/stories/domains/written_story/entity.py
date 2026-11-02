from app.shared.common import Entity


class WrittenStory(Entity):
    title: str
    description: str | None
    criteria: list[str]
