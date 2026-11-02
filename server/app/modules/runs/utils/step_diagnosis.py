from app.modules.runs.domains.failed_request.entity import FailedRequest
from app.modules.runs.domains.step_diagnosis.entity import StepDiagnosis
from app.modules.runs.domains.step_report.entity import StepReport
from app.modules.runs.typing.constants.run_report import FAILING_RESULT_STATUSES
from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.shared.masking import SecretMasker


def remove_query(url: str) -> str:
    return url.split("?", 1)[0].split("#", 1)[0]


def build_step_diagnosis(step_report: StepReport, masker: SecretMasker) -> StepDiagnosis | None:
    if step_report.page_url is None and not step_report.console_errors and not step_report.failed_requests:
        return None
    return StepDiagnosis(
        page_url=None if step_report.page_url is None else masker.mask(remove_query(step_report.page_url)),
        console_errors=[masker.mask(console_error) for console_error in step_report.console_errors],
        failed_requests=[
            FailedRequest(
                method=failed_request.method.upper(),
                path=masker.mask(remove_query(failed_request.path)),
                status=failed_request.status,
                excerpt=masker.mask_optional(failed_request.excerpt),
            )
            for failed_request in step_report.failed_requests
        ],
    )


def select_suspected_cause(
    status: ResultStatus, suspected_cause: SuspectedCause | None, cause_reason: str | None, masker: SecretMasker
) -> tuple[SuspectedCause | None, str | None]:
    if status not in FAILING_RESULT_STATUSES:
        return None, None
    return suspected_cause, masker.mask_optional(cause_reason)
