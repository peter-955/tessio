from datetime import datetime
from uuid import UUID, uuid7

from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.criteria_change.entity import CriteriaChange
from app.modules.stories.domains.criteria_merge.entity import CriteriaMerge
from app.modules.stories.typing.constants import CRITERION_CODE_PREFIX


def merge_acceptance_criteria(
    project_id: UUID,
    story_id: UUID,
    existing: list[AcceptanceCriterion],
    parsed_texts: list[str],
    now: datetime,
) -> CriteriaMerge:
    existing_by_position = {criterion.position: criterion for criterion in existing}
    criteria_to_save: list[AcceptanceCriterion] = []
    added_criterion_ids: set[UUID] = set()
    changed_criterion_ids: set[UUID] = set()
    removed_criterion_ids: set[UUID] = set()
    for position, text in enumerate(parsed_texts, start=1):
        current = existing_by_position.get(position)
        if current is None:
            created = AcceptanceCriterion(
                id=uuid7(),
                story_id=story_id,
                position=position,
                code=f"{CRITERION_CODE_PREFIX}{position}",
                text=text,
                removed_at=None,
                created_at=now,
            )
            criteria_to_save.append(created)
            added_criterion_ids.add(created.id)
        elif current.text != text or current.is_removed:
            criteria_to_save.append(current.model_copy(update={"text": text, "removed_at": None}))
            changed_criterion_ids.add(current.id)
    for criterion in sorted(existing, key=lambda criterion: criterion.position):
        if criterion.position > len(parsed_texts) and not criterion.is_removed:
            criteria_to_save.append(criterion.model_copy(update={"removed_at": now}))
            removed_criterion_ids.add(criterion.id)
    return CriteriaMerge(
        criteria_to_save=criteria_to_save,
        change=CriteriaChange(
            project_id=project_id,
            story_id=story_id,
            added_criterion_ids=frozenset(added_criterion_ids),
            changed_criterion_ids=frozenset(changed_criterion_ids),
            removed_criterion_ids=frozenset(removed_criterion_ids),
        ),
    )
