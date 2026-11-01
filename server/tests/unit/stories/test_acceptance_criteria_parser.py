import pytest
from pydantic import JsonValue

from app.modules.stories import parse_acceptance_criteria
from app.modules.stories.typing.enums import CriteriaSource
from tests.unit.stories.adf_fixtures import load_adf_fixture


@pytest.mark.parametrize(
    ("fixture_name", "expected_texts", "expected_source"),
    [
        (
            "heading_bullet_list",
            ["Card payment succeeds", "Declined card shows an error"],
            CriteriaSource.MARKED_LIST,
        ),
        (
            "bold_paragraph_marker_ordered_list",
            ["A reset email is sent", "The link expires after 30 minutes"],
            CriteriaSource.MARKED_LIST,
        ),
        (
            "no_marker_first_list",
            ["Orders are listed newest first", "Each order shows its total"],
            CriteriaSource.FIRST_LIST,
        ),
        ("marker_without_list", [], CriteriaSource.MARKED_LIST),
        (
            "nested_items_mentions_hard_break",
            [
                "@Alice approves the refund\nwithin 2 days 🎉\n- Email is sent\n- Status becomes REFUNDED",
                "See https://docs.shop.test/refunds",
            ],
            CriteriaSource.MARKED_LIST,
        ),
        (
            "list_in_panel",
            ["Results match the search text", "No results shows an empty state"],
            CriteriaSource.MARKED_LIST,
        ),
        (
            "task_list",
            ["Le panier se vide", "Le total est mis à jour\n- TVA incluse"],
            CriteriaSource.MARKED_LIST,
        ),
        ("next_heading_before_list", [], CriteriaSource.MARKED_LIST),
    ],
)
def test_each_fixture_is_parsed(fixture_name: str, expected_texts: list[str], expected_source: CriteriaSource) -> None:
    parsed = parse_acceptance_criteria(load_adf_fixture(fixture_name))

    assert parsed.texts == expected_texts
    assert parsed.source is expected_source


@pytest.mark.parametrize("description", [None, "Plain text description", 42, True, [1, 2], {}, {"content": "x"}])
def test_a_description_without_a_document_gives_no_criteria(description: JsonValue) -> None:
    parsed = parse_acceptance_criteria(description)

    assert parsed.texts == []
    assert parsed.source is CriteriaSource.NONE


def test_garbage_nodes_never_raise() -> None:
    description: JsonValue = {
        "type": "doc",
        "content": [
            1,
            None,
            {"type": 5, "content": [{"type": "text", "text": 7}]},
            {"type": "heading", "attrs": "level", "content": [{"type": "text", "text": "Acceptance criteria"}]},
            {"type": "bulletList", "content": "items"},
            {"type": "bulletList", "content": [{"type": "listItem", "content": [{"type": "mention", "attrs": 3}]}]},
        ],
    }

    parsed = parse_acceptance_criteria(description)

    assert parsed.texts == []
    assert parsed.source is CriteriaSource.MARKED_LIST


@pytest.mark.parametrize(
    "marker", ["Critères d'acceptation", "CRITERES D'ACCEPTATION", "Tiêu chí chấp nhận", "acceptance criteria"]
)
def test_marker_matches_every_language_without_case(marker: str) -> None:
    description: JsonValue = {
        "type": "doc",
        "content": [
            {"type": "bulletList", "content": [_build_list_item("Not this one")]},
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": marker}]},
            {"type": "orderedList", "content": [_build_list_item("Le paiement est accepté")]},
        ],
    }

    parsed = parse_acceptance_criteria(description)

    assert parsed.texts == ["Le paiement est accepté"]
    assert parsed.source is CriteriaSource.MARKED_LIST


def test_a_long_paragraph_mentioning_the_marker_is_not_a_marker() -> None:
    sentence = "The acceptance criteria for this story are agreed with the product owner during refinement."
    description: JsonValue = {
        "type": "doc",
        "content": [
            {"type": "bulletList", "content": [_build_list_item("First list item")]},
            {"type": "paragraph", "content": [{"type": "text", "text": sentence}]},
            {"type": "bulletList", "content": [_build_list_item("Second list item")]},
        ],
    }

    parsed = parse_acceptance_criteria(description)

    assert parsed.texts == ["First list item"]
    assert parsed.source is CriteriaSource.FIRST_LIST


def test_a_paragraph_marker_stops_at_any_heading() -> None:
    description: JsonValue = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Acceptance criteria"}]},
            {"type": "heading", "attrs": {"level": 6}, "content": [{"type": "text", "text": "Design"}]},
            {"type": "bulletList", "content": [_build_list_item("Design item")]},
        ],
    }

    parsed = parse_acceptance_criteria(description)

    assert parsed.texts == []
    assert parsed.source is CriteriaSource.MARKED_LIST


def _build_list_item(text: str) -> JsonValue:
    return {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]}
