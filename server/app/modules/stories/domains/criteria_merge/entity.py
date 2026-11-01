from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.criteria_change.entity import CriteriaChange
from app.shared.common import Entity


class CriteriaMerge(Entity):
    criteria_to_save: list[AcceptanceCriterion]
    change: CriteriaChange
