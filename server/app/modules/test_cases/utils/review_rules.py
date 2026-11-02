from app.modules.test_cases.domains.review_comment.repository import ReviewCommentRepository
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.errors import ReviewCommentsOpenError, ReviewerIsAuthorError
from app.modules.test_cases.ports.review_policy_reader import ReviewPolicyReader
from app.shared.permissions import Actor


async def require_separate_reviewer(
    review_policy_reader: ReviewPolicyReader, test_case: TestCase, version: TestCaseVersion, actor: Actor
) -> None:
    if version.created_by != actor.user_id:
        return
    if await review_policy_reader.is_requiring_separate_reviewer(test_case.project_id):
        raise ReviewerIsAuthorError


async def require_no_open_review_comments(
    review_comment_repository: ReviewCommentRepository, test_case: TestCase
) -> None:
    open_count = await review_comment_repository.count_open(test_case.id)
    if open_count:
        raise ReviewCommentsOpenError(open_count)
