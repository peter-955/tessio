from fastapi import Request

from app.modules.failures.usecases.assign_failure import AssignFailureUseCase
from app.modules.failures.usecases.change_failure_cause import ChangeFailureCauseUseCase
from app.modules.failures.usecases.change_failure_status import ChangeFailureStatusUseCase
from app.modules.failures.usecases.get_failure import GetFailureUseCase
from app.modules.failures.usecases.list_failures import ListFailuresUseCase
from app.modules.failures.usecases.preview_jira_issue import PreviewJiraIssueUseCase
from app.modules.failures.usecases.request_jira_issue import RequestJiraIssueUseCase


def get_list_failures(request: Request) -> ListFailuresUseCase:
    use_case: ListFailuresUseCase = request.app.state.container.list_failures
    return use_case


def get_get_failure(request: Request) -> GetFailureUseCase:
    use_case: GetFailureUseCase = request.app.state.container.get_failure
    return use_case


def get_change_failure_status(request: Request) -> ChangeFailureStatusUseCase:
    use_case: ChangeFailureStatusUseCase = request.app.state.container.change_failure_status
    return use_case


def get_assign_failure(request: Request) -> AssignFailureUseCase:
    use_case: AssignFailureUseCase = request.app.state.container.assign_failure
    return use_case


def get_change_failure_cause(request: Request) -> ChangeFailureCauseUseCase:
    use_case: ChangeFailureCauseUseCase = request.app.state.container.change_failure_cause
    return use_case


def get_request_jira_issue(request: Request) -> RequestJiraIssueUseCase:
    use_case: RequestJiraIssueUseCase = request.app.state.container.request_jira_issue
    return use_case


def get_preview_jira_issue(request: Request) -> PreviewJiraIssueUseCase:
    use_case: PreviewJiraIssueUseCase = request.app.state.container.preview_jira_issue
    return use_case
