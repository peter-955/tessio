from app.modules.labels.domains.label.entity import Label
from app.shared.common import Entity


class LabelSummary(Entity):
    label: Label
    case_count: int
