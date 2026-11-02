from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion
from app.modules.stories.domains.project_sync_state.entity import ProjectSyncState
from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.sprint_overview.entity import SprintOverview
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.domains.story_summary.entity import StorySummary
from app.modules.stories.models.acceptance_criterion_response import AcceptanceCriterionResponse
from app.modules.stories.models.project_sync_state_response import ProjectSyncStateResponse
from app.modules.stories.models.sprint_reference_response import SprintReferenceResponse
from app.modules.stories.models.sprint_response import SprintResponse
from app.modules.stories.models.story_detail_response import StoryDetailResponse
from app.modules.stories.models.story_summary_response import StorySummaryResponse
from app.modules.stories.typing.enums import TestStatus
from app.modules.stories.utils.plain_text_document import read_plain_text


def build_sprint_response(overview: SprintOverview) -> SprintResponse:
    sprint = overview.sprint
    return SprintResponse(
        id=sprint.id,
        jira_sprint_id=sprint.jira_sprint_id,
        name=sprint.name,
        state=sprint.state,
        start_at=sprint.start_at,
        end_at=sprint.end_at,
        complete_at=sprint.complete_at,
        story_count=overview.story_count,
        synced_at=sprint.synced_at,
    )


def build_sprint_reference_response(sprint: Sprint) -> SprintReferenceResponse:
    return SprintReferenceResponse(id=sprint.id, name=sprint.name, state=sprint.state)


def build_story_summary_response(summary: StorySummary) -> StorySummaryResponse:
    story = summary.story
    return StorySummaryResponse(
        id=story.id,
        jira_key=story.jira_key,
        jira_url=story.jira_url,
        title=story.title,
        jira_status=story.jira_status,
        jira_issue_type=story.jira_issue_type,
        test_status=story.test_status,
        sprint_id=story.sprint_id,
        sprint_name=summary.sprint_name,
        criterion_count=summary.criterion_count,
        synced_at=story.synced_at,
        jira_missing_at=story.jira_missing_at,
        source=story.source,
    )


def build_acceptance_criterion_response(criterion: AcceptanceCriterion) -> AcceptanceCriterionResponse:
    return AcceptanceCriterionResponse(
        id=criterion.id,
        code=criterion.code,
        position=criterion.position,
        text=criterion.text,
        removed_at=criterion.removed_at,
        is_removed=criterion.is_removed,
    )


def build_story_detail_response(detail: StoryDetail) -> StoryDetailResponse:
    story = detail.story
    return StoryDetailResponse(
        id=story.id,
        jira_key=story.jira_key,
        jira_url=story.jira_url,
        title=story.title,
        jira_status=story.jira_status,
        jira_issue_type=story.jira_issue_type,
        test_status=story.test_status,
        synced_at=story.synced_at,
        jira_missing_at=story.jira_missing_at,
        description=story.description,
        sprint=None if detail.sprint is None else build_sprint_reference_response(detail.sprint),
        criteria=[
            build_acceptance_criterion_response(criterion)
            for criterion in sorted(detail.criteria, key=lambda criterion: criterion.position)
        ],
        available_test_statuses=[status for status in TestStatus if status in detail.available_test_statuses],
        test_status_changed_at=story.test_status_changed_at,
        jira_updated_at=story.jira_updated_at,
        source=story.source,
        description_text=read_plain_text(story.description) if story.is_written_in_tessio else None,
    )


def build_project_sync_state_response(state: ProjectSyncState) -> ProjectSyncStateResponse:
    return ProjectSyncStateResponse(
        status=state.status,
        queued_at=state.queued_at,
        started_at=state.started_at,
        finished_at=state.finished_at,
        last_succeeded_at=state.last_succeeded_at,
        error_code=state.error_code,
    )
