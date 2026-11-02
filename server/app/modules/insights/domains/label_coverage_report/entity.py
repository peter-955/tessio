from app.modules.insights.domains.case_share_counts.entity import CaseShareCounts
from app.modules.insights.domains.label_coverage.entity import LabelCoverage
from app.shared.common import Entity


class LabelCoverageReport(Entity):
    labels: list[LabelCoverage]
    unlabelled: CaseShareCounts
    total: CaseShareCounts
