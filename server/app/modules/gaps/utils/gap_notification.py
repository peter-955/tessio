from uuid import UUID

from app.modules.gaps.domains.gap.entity import Gap
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.notifications import GapAssignedPayload
from app.shared.events import LiveEvent, LiveEventType
from app.shared.permissions import ProjectRole


def build_gap_assigned_payload(view: GapView) -> GapAssignedPayload:
    return GapAssignedPayload(
        gap_id=view.gap.id,
        story_id=view.gap.story_id,
        story_jira_key=view.story_jira_key,
        question=view.gap.question,
    )


def build_gap_changed_event(gap: Gap) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.GAP_CHANGED,
        project_id=gap.project_id,
        ids={"gapId": str(gap.id), "storyId": str(gap.story_id)},
    )


def list_recipient_ids(gap: Gap) -> frozenset[UUID]:
    return frozenset() if gap.assignee_id is None else frozenset({gap.assignee_id})


def list_recipient_roles(gap: Gap) -> frozenset[ProjectRole]:
    if gap.assignee_id is not None or gap.assignee_role is None:
        return frozenset()
    return frozenset({gap.assignee_role})
