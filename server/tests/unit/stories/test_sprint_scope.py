from datetime import UTC, datetime, timedelta

import pytest

from app.modules.jira import JiraIssue, JiraSprint, JiraSprintState
from app.modules.stories.utils.sprint_scope import assign_stories_to_sprints, is_sprint_in_scope

NOW = datetime(2026, 11, 1, 12, tzinfo=UTC)


def build_sprint(
    sprint_id: int,
    state: JiraSprintState,
    complete_at: datetime | None = None,
    end_at: datetime | None = None,
) -> JiraSprint:
    return JiraSprint(
        id=sprint_id, name=f"Sprint {sprint_id}", state=state, start_at=None, end_at=end_at, complete_at=complete_at
    )


def build_issue(issue_id: str, issue_type_name: str = "Story", is_subtask: bool = False) -> JiraIssue:
    return JiraIssue(
        id=issue_id,
        key=f"SHOP-{issue_id}",
        summary=f"Issue {issue_id}",
        description=None,
        status_name="To Do",
        issue_type_name=issue_type_name,
        is_subtask=is_subtask,
        updated_at=NOW,
    )


@pytest.mark.parametrize("state", [JiraSprintState.ACTIVE, JiraSprintState.FUTURE])
def test_active_and_future_sprints_are_in_scope(state: JiraSprintState) -> None:
    assert is_sprint_in_scope(build_sprint(1, state), NOW) is True


@pytest.mark.parametrize(("closed_days_ago", "is_expected_in_scope"), [(29, True), (30, True), (31, False)])
def test_closed_sprints_count_for_thirty_days(closed_days_ago: int, is_expected_in_scope: bool) -> None:
    sprint = build_sprint(1, JiraSprintState.CLOSED, complete_at=NOW - timedelta(days=closed_days_ago))

    assert is_sprint_in_scope(sprint, NOW) is is_expected_in_scope


def test_a_closed_sprint_without_complete_at_falls_back_to_end_at() -> None:
    recent = build_sprint(1, JiraSprintState.CLOSED, end_at=NOW - timedelta(days=29))
    old = build_sprint(2, JiraSprintState.CLOSED, end_at=NOW - timedelta(days=31))
    undated = build_sprint(3, JiraSprintState.CLOSED)

    assert is_sprint_in_scope(recent, NOW) is True
    assert is_sprint_in_scope(old, NOW) is False
    assert is_sprint_in_scope(undated, NOW) is False


def test_complete_at_wins_over_end_at() -> None:
    sprint = build_sprint(
        1, JiraSprintState.CLOSED, complete_at=NOW - timedelta(days=31), end_at=NOW - timedelta(days=1)
    )

    assert is_sprint_in_scope(sprint, NOW) is False


def test_an_issue_in_several_sprints_goes_to_the_preferred_one() -> None:
    older_closed = build_sprint(1, JiraSprintState.CLOSED, complete_at=NOW - timedelta(days=20))
    newer_closed = build_sprint(2, JiraSprintState.CLOSED, complete_at=NOW - timedelta(days=5))
    future = build_sprint(3, JiraSprintState.FUTURE)
    active = build_sprint(4, JiraSprintState.ACTIVE)
    in_all = build_issue("1")
    closed_and_future = build_issue("2")
    both_closed = build_issue("3")

    fetched = assign_stories_to_sprints(
        {
            active: [in_all],
            older_closed: [in_all, closed_and_future, both_closed],
            future: [in_all, closed_and_future],
            newer_closed: [in_all, both_closed],
        }
    )

    assert {issue_id: story.jira_sprint_id for issue_id, story in fetched.items()} == {"1": 4, "2": 3, "3": 2}
    assert fetched["1"].issue == in_all


def test_epics_and_sub_tasks_are_skipped() -> None:
    active = build_sprint(1, JiraSprintState.ACTIVE)

    fetched = assign_stories_to_sprints(
        {
            active: [
                build_issue("1"),
                build_issue("2", issue_type_name="Epic"),
                build_issue("3", issue_type_name="EPIC"),
                build_issue("4", issue_type_name="Sub-task", is_subtask=True),
                build_issue("5", issue_type_name="Bug"),
            ]
        }
    )

    assert sorted(fetched) == ["1", "5"]
