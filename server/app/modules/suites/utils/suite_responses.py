from app.modules.suites.domains.suite_detail.entity import SuiteDetail
from app.modules.suites.domains.suite_run_reference.entity import SuiteRunReference
from app.modules.suites.domains.suite_summary.entity import SuiteSummary
from app.modules.suites.models.suite_case_response import SuiteCaseResponse
from app.modules.suites.models.suite_detail_response import SuiteDetailResponse
from app.modules.suites.models.suite_run_reference_response import SuiteRunReferenceResponse
from app.modules.suites.models.suite_summary_response import SuiteSummaryResponse


def build_suite_run_reference_response(run: SuiteRunReference | None) -> SuiteRunReferenceResponse | None:
    return None if run is None else SuiteRunReferenceResponse.model_validate(run.model_dump())


def build_suite_summary_response(summary: SuiteSummary) -> SuiteSummaryResponse:
    return SuiteSummaryResponse(
        id=summary.suite.id,
        name=summary.suite.name,
        description=summary.suite.description,
        case_count=summary.case_count,
        ready_case_count=summary.ready_case_count,
        archived_at=summary.suite.archived_at,
        created_at=summary.suite.created_at,
        last_run=build_suite_run_reference_response(summary.last_run),
    )


def build_suite_detail_response(detail: SuiteDetail) -> SuiteDetailResponse:
    return SuiteDetailResponse(
        id=detail.suite.id,
        name=detail.suite.name,
        description=detail.suite.description,
        archived_at=detail.suite.archived_at,
        created_by=detail.suite.created_by,
        created_at=detail.suite.created_at,
        case_count=len(detail.cases),
        ready_case_count=sum(1 for case in detail.cases if case.is_runnable),
        cases=[SuiteCaseResponse(**case.model_dump(), is_runnable=case.is_runnable) for case in detail.cases],
        last_run=build_suite_run_reference_response(detail.last_run),
        running_run=build_suite_run_reference_response(detail.running_run),
    )
