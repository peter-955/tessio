from app.shared.common import Entity


class ReportLabel(Entity):
    source_id: str
    label: str
    file_stem: str
