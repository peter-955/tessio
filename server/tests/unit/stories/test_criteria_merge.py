from datetime import UTC, datetime, timedelta
from uuid import uuid7

from app.modules.stories import AcceptanceCriterion
from app.modules.stories.utils.criteria_merge import merge_acceptance_criteria

PROJECT_ID = uuid7()
STORY_ID = uuid7()
SYNCED_AT = datetime(2026, 10, 1, tzinfo=UTC)
NOW = SYNCED_AT + timedelta(days=1)


def build_criterion(position: int, text: str, removed_at: datetime | None = None) -> AcceptanceCriterion:
    return AcceptanceCriterion(
        id=uuid7(),
        story_id=STORY_ID,
        position=position,
        code=f"AC{position}",
        text=text,
        removed_at=removed_at,
        created_at=SYNCED_AT,
    )


def test_the_first_sync_adds_every_criterion() -> None:
    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, [], ["Pay by card", "See receipt"], NOW)

    assert [(criterion.position, criterion.code, criterion.text) for criterion in merge.criteria_to_save] == [
        (1, "AC1", "Pay by card"),
        (2, "AC2", "See receipt"),
    ]
    assert all(criterion.created_at == NOW and criterion.removed_at is None for criterion in merge.criteria_to_save)
    assert merge.change.added_criterion_ids == {criterion.id for criterion in merge.criteria_to_save}
    assert merge.change.changed_criterion_ids == frozenset()
    assert merge.change.removed_criterion_ids == frozenset()
    assert merge.change.has_changed_or_removed is False


def test_a_text_change_updates_the_row_and_flags_it() -> None:
    first = build_criterion(1, "Pay by card")
    second = build_criterion(2, "See receipt")

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, [first, second], ["Pay by card", "Email receipt"], NOW)

    assert merge.criteria_to_save == [second.model_copy(update={"text": "Email receipt"})]
    assert merge.change.changed_criterion_ids == {second.id}
    assert merge.change.added_criterion_ids == frozenset()
    assert merge.change.has_changed_or_removed is True


def test_a_middle_insert_flags_every_later_position() -> None:
    criteria = [build_criterion(1, "A"), build_criterion(2, "B"), build_criterion(3, "C")]

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, criteria, ["A", "New", "B", "C"], NOW)

    assert merge.change.changed_criterion_ids == {criteria[1].id, criteria[2].id}
    assert len(merge.change.added_criterion_ids) == 1
    added = next(criterion for criterion in merge.criteria_to_save if criterion.id in merge.change.added_criterion_ids)
    assert (added.position, added.code, added.text) == (4, "AC4", "C")
    assert [criterion.text for criterion in merge.criteria_to_save if criterion.position in {2, 3}] == ["New", "B"]


def test_deleting_the_last_criterion_sets_removed_at() -> None:
    criteria = [build_criterion(1, "A"), build_criterion(2, "B")]

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, criteria, ["A"], NOW)

    assert merge.criteria_to_save == [criteria[1].model_copy(update={"removed_at": NOW})]
    assert merge.change.removed_criterion_ids == {criteria[1].id}
    assert merge.change.has_changed_or_removed is True


def test_a_removed_criterion_that_comes_back_is_restored() -> None:
    criteria = [build_criterion(1, "A"), build_criterion(2, "B", removed_at=SYNCED_AT)]

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, criteria, ["A", "B"], NOW)

    assert merge.criteria_to_save == [criteria[1].model_copy(update={"removed_at": None})]
    assert merge.change.changed_criterion_ids == {criteria[1].id}


def test_an_already_removed_criterion_is_not_removed_again() -> None:
    criteria = [build_criterion(1, "A"), build_criterion(2, "B", removed_at=SYNCED_AT)]

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, criteria, ["A"], NOW)

    assert merge.criteria_to_save == []
    assert merge.change.removed_criterion_ids == frozenset()


def test_unchanged_criteria_give_an_empty_change() -> None:
    criteria = [build_criterion(1, "A"), build_criterion(2, "B")]

    merge = merge_acceptance_criteria(PROJECT_ID, STORY_ID, criteria, ["A", "B"], NOW)

    assert merge.criteria_to_save == []
    assert merge.change.added_criterion_ids == frozenset()
    assert merge.change.changed_criterion_ids == frozenset()
    assert merge.change.removed_criterion_ids == frozenset()
    assert (merge.change.project_id, merge.change.story_id) == (PROJECT_ID, STORY_ID)
