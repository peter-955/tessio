from datetime import datetime

from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.typing.constants import SEVERITY_RANK


def build_my_gap_sort_key(view: GapView) -> tuple[int, str, datetime]:
    return SEVERITY_RANK[view.gap.severity], view.story_jira_key, view.gap.created_at
