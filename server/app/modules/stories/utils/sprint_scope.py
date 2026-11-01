from collections.abc import Mapping
from datetime import datetime

from app.modules.jira import JiraIssue, JiraSprint, JiraSprintState
from app.modules.stories.domains.fetched_story.entity import FetchedStory
from app.modules.stories.typing.constants import (
    CLOSED_SPRINT_SYNC_WINDOW,
    EPIC_ISSUE_TYPE_NAME,
    JIRA_SPRINT_STATE_PRECEDENCE,
)


def is_sprint_in_scope(jira_sprint: JiraSprint, now: datetime) -> bool:
    if jira_sprint.state in {JiraSprintState.ACTIVE, JiraSprintState.FUTURE}:
        return True
    closed_at = jira_sprint.complete_at or jira_sprint.end_at
    return closed_at is not None and closed_at >= now - CLOSED_SPRINT_SYNC_WINDOW


def assign_stories_to_sprints(issues_by_sprint: Mapping[JiraSprint, list[JiraIssue]]) -> dict[str, FetchedStory]:
    fetched_stories: dict[str, FetchedStory] = {}
    chosen_sprints: dict[str, JiraSprint] = {}
    for jira_sprint, issues in issues_by_sprint.items():
        for issue in issues:
            if not _is_story_issue(issue):
                continue
            chosen_sprint = chosen_sprints.get(issue.id)
            if chosen_sprint is not None and not _is_preferred(jira_sprint, chosen_sprint):
                continue
            chosen_sprints[issue.id] = jira_sprint
            fetched_stories[issue.id] = FetchedStory(issue=issue, jira_sprint_id=jira_sprint.id)
    return fetched_stories


def _is_story_issue(issue: JiraIssue) -> bool:
    return not issue.is_subtask and issue.issue_type_name.casefold() != EPIC_ISSUE_TYPE_NAME


def _is_preferred(candidate: JiraSprint, current: JiraSprint) -> bool:
    candidate_rank = JIRA_SPRINT_STATE_PRECEDENCE[candidate.state]
    current_rank = JIRA_SPRINT_STATE_PRECEDENCE[current.state]
    if candidate_rank != current_rank:
        return candidate_rank > current_rank
    if candidate.state is not JiraSprintState.CLOSED:
        return False
    candidate_closed_at = candidate.complete_at or candidate.end_at
    current_closed_at = current.complete_at or current.end_at
    if candidate_closed_at is None:
        return False
    return current_closed_at is None or candidate_closed_at > current_closed_at
