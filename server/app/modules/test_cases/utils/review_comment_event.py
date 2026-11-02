from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.shared.events import LiveEvent, LiveEventType


def build_review_comment_changed_event(test_case: TestCase, comment: ReviewComment) -> LiveEvent:
    return LiveEvent(
        type=LiveEventType.REVIEW_COMMENT_CHANGED,
        project_id=test_case.project_id,
        ids={
            "testCaseId": str(test_case.id),
            "code": test_case.code,
            "storyId": str(test_case.story_id),
            "commentId": str(comment.id),
        },
    )
