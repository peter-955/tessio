from app.modules.gaps.domains.gap.entity import Gap
from app.modules.users import UserStatus
from app.shared.common import Entity


class GapView(Entity):
    gap: Gap
    project_key: str
    project_name: str
    story_jira_key: str
    story_title: str
    target_ref: str | None
    assignee_name: str | None
    assignee_status: UserStatus | None
    raised_by_name: str
    answered_by_name: str | None
    reopened_by_name: str | None
