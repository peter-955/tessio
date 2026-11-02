from app.modules.test_cases.domains.review_comment_view.entity import ReviewCommentView
from app.modules.test_cases.models.review_comment_response import ReviewCommentResponse


def build_review_comment_response(view: ReviewCommentView) -> ReviewCommentResponse:
    comment = view.comment
    return ReviewCommentResponse(
        id=comment.id,
        version_id=comment.version_id,
        version_number=view.version_number,
        step_order=comment.step_order,
        body=comment.body,
        author_id=comment.author_id,
        author_name=view.author_name,
        created_at=comment.created_at,
        is_resolved=comment.is_resolved,
        resolved_at=comment.resolved_at,
        resolved_by=comment.resolved_by,
        resolved_by_name=view.resolved_by_name,
    )
