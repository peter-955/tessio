from uuid import UUID

from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.runs import CriterionStatus
from app.shared.common import Entity


class CriterionTrace(Entity):
    criterion: TracedCriterion
    status: CriterionStatus
    linked_case_ids: list[UUID]
