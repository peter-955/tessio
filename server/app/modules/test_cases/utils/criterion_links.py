from collections.abc import Collection, Sequence
from uuid import UUID

from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.errors import CriterionNotLinkableError


def require_linkable(
    requested_ids: Sequence[UUID], story_criteria: Sequence[CaseCriterion], previous_ids: Collection[UUID]
) -> list[UUID]:
    criteria_by_id = {criterion.id: criterion for criterion in story_criteria}
    linkable_ids = list(dict.fromkeys(requested_ids))
    for criterion_id in linkable_ids:
        criterion = criteria_by_id.get(criterion_id)
        if criterion is None or (criterion.is_removed and criterion_id not in previous_ids):
            raise CriterionNotLinkableError
    return linkable_ids
