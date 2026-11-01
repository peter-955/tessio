from collections.abc import Sequence

from app.modules.insights.domains.criterion_trace.entity import CriterionTrace
from app.modules.insights.domains.traced_story.entity import TracedStory
from app.modules.insights.domains.uncovered_criterion_item.entity import UncoveredCriterionItem
from app.modules.insights.domains.uncovered_criterion_list.entity import UncoveredCriterionList
from app.modules.runs import CriterionStatus


def list_uncovered_criteria(
    stories: Sequence[TracedStory], traces: Sequence[CriterionTrace], limit: int
) -> UncoveredCriterionList:
    story_rank = {story.id: rank for rank, story in enumerate(stories)}
    stories_by_id = {story.id: story for story in stories}
    uncovered = sorted(
        (
            trace.criterion
            for trace in traces
            if trace.criterion.is_active
            and trace.status is CriterionStatus.UNCOVERED
            and trace.criterion.story_id in stories_by_id
        ),
        key=lambda criterion: (story_rank[criterion.story_id], criterion.position),
    )
    items = [
        UncoveredCriterionItem(
            criterion_id=criterion.id,
            code=criterion.code,
            text=criterion.text,
            story_jira_key=stories_by_id[criterion.story_id].jira_key,
            story_title=stories_by_id[criterion.story_id].title,
        )
        for criterion in uncovered[:limit]
    ]
    return UncoveredCriterionList(total_count=len(uncovered), items=items)
