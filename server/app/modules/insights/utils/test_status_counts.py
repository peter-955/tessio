from collections import Counter
from collections.abc import Sequence

from app.modules.insights.domains.test_status_counts.entity import TestStatusCounts
from app.modules.insights.domains.traced_story.entity import TracedStory
from app.modules.stories import TestStatus


def count_test_statuses(stories: Sequence[TracedStory]) -> TestStatusCounts:
    counts = Counter(story.test_status for story in stories)
    return TestStatusCounts(
        not_started=counts[TestStatus.NOT_STARTED],
        ready_for_test=counts[TestStatus.READY_FOR_TEST],
        in_test=counts[TestStatus.IN_TEST],
        passed=counts[TestStatus.PASSED],
        failed=counts[TestStatus.FAILED],
    )
