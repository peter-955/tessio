from app.shared.common import Entity


class ExecutorCount(Entity):
    executor: str
    count: int
