from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.criterion_trace.entity import CriterionTrace
from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_story.entity import TracedStory
from app.shared.common import Entity


class Traceability(Entity):
    story: TracedStory
    criteria: list[CriterionTrace]
    cases: list[TracedCase]
    coverage: CoverageCount
