from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.domains.case_import_preview.entity import CaseImportPreview
from app.modules.test_cases.domains.case_import_result.entity import CaseImportResult
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.modules.test_cases.domains.test_case_detail.entity import TestCaseDetail
from app.modules.test_cases.domains.test_case_summary.entity import TestCaseSummary
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_file_detail.entity import TestFileDetail
from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.models.case_import_preview_item_response import CaseImportPreviewItemResponse
from app.modules.test_cases.models.case_import_preview_response import CaseImportPreviewResponse
from app.modules.test_cases.models.case_import_result_response import CaseImportResultResponse
from app.modules.test_cases.models.case_import_skip_response import CaseImportSkipResponse
from app.modules.test_cases.models.case_story_response import CaseStoryResponse
from app.modules.test_cases.models.imported_case_code_response import ImportedCaseCodeResponse
from app.modules.test_cases.models.linked_criterion_response import LinkedCriterionResponse
from app.modules.test_cases.models.test_case_detail_response import TestCaseDetailResponse
from app.modules.test_cases.models.test_case_summary_response import TestCaseSummaryResponse
from app.modules.test_cases.models.test_case_version_response import TestCaseVersionResponse
from app.modules.test_cases.models.test_file_response import TestFileResponse
from app.modules.test_cases.models.test_file_version_response import TestFileVersionResponse
from app.modules.test_cases.models.test_step_response import TestStepResponse


def build_test_step_response(step: TestStep) -> TestStepResponse:
    return TestStepResponse(order=step.order, action=step.action, expected=step.expected)


def build_test_case_summary_response(summary: TestCaseSummary) -> TestCaseSummaryResponse:
    test_case = summary.test_case
    return TestCaseSummaryResponse(
        id=test_case.id,
        code=test_case.code,
        story_id=test_case.story_id,
        story_key=summary.story_key,
        title=test_case.title,
        priority=test_case.priority,
        status=test_case.status,
        current_version_id=test_case.current_version_id,
        current_version_number=summary.current_version_number,
        step_count=summary.step_count,
        criterion_ids=summary.criterion_ids,
        needs_review=test_case.is_needing_review,
        needs_review_at=test_case.needs_review_at,
        last_saved_at=summary.last_saved_at,
    )


def build_test_case_version_response(version: TestCaseVersion) -> TestCaseVersionResponse:
    return TestCaseVersionResponse(
        id=version.id,
        number=version.number,
        title=version.title,
        priority=version.priority,
        business_value=version.business_value,
        preconditions=version.preconditions,
        steps=[build_test_step_response(step) for step in version.steps],
        criterion_ids=version.criterion_ids,
        data_keys=version.data_keys,
        file_version_ids=version.file_version_ids,
        created_by=version.created_by,
        created_at=version.created_at,
    )


def build_linked_criterion_response(criterion: CaseCriterion) -> LinkedCriterionResponse:
    return LinkedCriterionResponse(
        id=criterion.id, code=criterion.code, text=criterion.text, is_removed=criterion.is_removed
    )


def build_case_story_response(story: CaseStory) -> CaseStoryResponse:
    return CaseStoryResponse(id=story.id, jira_key=story.jira_key, title=story.title)


def build_test_file_version_response(detail: TestFileVersionDetail) -> TestFileVersionResponse:
    version = detail.version
    return TestFileVersionResponse(
        id=version.id,
        number=version.number,
        stored_file_id=version.stored_file_id,
        file_name=detail.file_name,
        content_type=detail.content_type,
        size=detail.size,
        created_by=version.created_by,
        created_at=version.created_at,
    )


def build_test_file_response(detail: TestFileDetail) -> TestFileResponse:
    return TestFileResponse(
        id=detail.test_file.id,
        key=detail.test_file.key,
        current_version=build_test_file_version_response(detail.current_version),
        version_count=detail.version_count,
    )


def build_test_case_detail_response(detail: TestCaseDetail) -> TestCaseDetailResponse:
    test_case = detail.test_case
    return TestCaseDetailResponse(
        id=test_case.id,
        code=test_case.code,
        story=build_case_story_response(detail.story),
        title=test_case.title,
        priority=test_case.priority,
        status=test_case.status,
        status_changed_at=test_case.status_changed_at,
        current_version=build_test_case_version_response(detail.version),
        criteria=[build_linked_criterion_response(criterion) for criterion in detail.criteria],
        files=[build_test_file_response(file) for file in detail.files],
        unknown_references=detail.unknown_references,
        needs_review=test_case.is_needing_review,
        needs_review_criterion_ids=test_case.needs_review_criterion_ids,
        needs_review_at=test_case.needs_review_at,
        reviewed_at=test_case.reviewed_at,
        reviewed_by=test_case.reviewed_by,
        created_by=test_case.created_by,
        created_at=test_case.created_at,
    )


def build_case_import_preview_response(preview: CaseImportPreview) -> CaseImportPreviewResponse:
    return CaseImportPreviewResponse(
        format=preview.format,
        items=[
            CaseImportPreviewItemResponse(
                index=item.index,
                location=item.location,
                story_key=item.story_key,
                title=item.title,
                priority=item.priority,
                step_count=item.step_count,
                criterion_codes=item.criterion_codes,
                unknown_criterion_codes=item.unknown_criterion_codes,
                is_duplicate=item.is_duplicate,
                problem=item.problem,
            )
            for item in preview.items
        ],
        skipped=[CaseImportSkipResponse(location=skip.location, reason=skip.reason) for skip in preview.skipped],
    )


def build_case_import_result_response(result: CaseImportResult) -> CaseImportResultResponse:
    return CaseImportResultResponse(
        created=[
            ImportedCaseCodeResponse(code=created.code, story_key=created.story_key, title=created.title)
            for created in result.created
        ]
    )
