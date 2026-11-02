from app.shared.common import Entity


class CaseShareCounts(Entity):
    case_count: int
    ready_count: int
    passed_count: int
