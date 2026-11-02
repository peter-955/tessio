from app.modules.test_cases.domains.review_comment.entity import ReviewComment
from app.shared.common import Entity


class ReviewCommentView(Entity):
    comment: ReviewComment
    version_number: int
    author_name: str
    resolved_by_name: str | None
