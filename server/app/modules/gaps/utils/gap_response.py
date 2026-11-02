from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.models.gap_response import GapResponse


def build_gap_response(view: GapView) -> GapResponse:
    gap = view.gap
    return GapResponse(
        id=gap.id,
        project_key=view.project_key,
        project_name=view.project_name,
        story_id=gap.story_id,
        story_jira_key=view.story_jira_key,
        story_title=view.story_title,
        target_type=gap.target_type,
        target_id=gap.target_id,
        target_ref=view.target_ref,
        type=gap.type,
        data_scope=gap.data_scope,
        severity=gap.severity,
        question=gap.question,
        status=gap.status,
        assignee_id=gap.assignee_id,
        assignee_name=view.assignee_name,
        assignee_status=view.assignee_status,
        assignee_role=gap.assignee_role,
        raised_by=gap.raised_by,
        raised_by_name=view.raised_by_name,
        is_raised_via_claude=gap.raised_via_token_id is not None,
        answer=gap.answer,
        answered_by=gap.answered_by,
        answered_by_name=view.answered_by_name,
        answered_at=gap.answered_at,
        is_answered_via_claude=gap.answered_via_token_id is not None,
        reopened_by_name=view.reopened_by_name,
        reopened_at=gap.reopened_at,
        created_at=gap.created_at,
    )
