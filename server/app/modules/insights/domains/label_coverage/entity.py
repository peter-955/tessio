from uuid import UUID

from app.modules.insights.domains.case_share_counts.entity import CaseShareCounts
from app.modules.labels import LabelColor
from app.shared.common import Entity


class LabelCoverage(Entity):
    label_id: UUID
    name: str
    color: LabelColor
    counts: CaseShareCounts
