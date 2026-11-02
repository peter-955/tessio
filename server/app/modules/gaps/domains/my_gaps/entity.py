from app.modules.gaps.domains.gap_assignee.entity import GapAssignee
from app.modules.gaps.domains.my_gap.entity import MyGap
from app.modules.gaps.domains.my_gap_story.entity import MyGapStory
from app.shared.common import Entity


class MyGaps(Entity):
    gaps: list[MyGap]
    gap_count: int
    stories: list[MyGapStory]
    assignees: list[GapAssignee]
    test_data_url: str | None
