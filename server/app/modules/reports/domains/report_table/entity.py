from app.shared.common import Entity


class ReportTable(Entity):
    headers: list[str]
    rows: list[list[str]]
