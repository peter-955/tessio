from app.modules.test_cases.domains.test_case_changes.entity import TestCaseChanges
from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion


def build_version_content(version: TestCaseVersion) -> TestCaseContent:
    return TestCaseContent(
        title=version.title,
        priority=version.priority,
        business_value=version.business_value,
        preconditions=version.preconditions,
        steps=version.steps,
        criterion_ids=version.criterion_ids,
        parameters=version.parameters,
        data_rows=version.data_rows,
    )


def merge_optional_text(current: str | None, change: str | None) -> str | None:
    if change is None:
        return current
    return change if change.strip() else None


def merge_changes(content: TestCaseContent, changes: TestCaseChanges) -> TestCaseContent:
    return TestCaseContent(
        title=content.title if changes.title is None else changes.title,
        priority=content.priority if changes.priority is None else changes.priority,
        business_value=merge_optional_text(content.business_value, changes.business_value),
        preconditions=merge_optional_text(content.preconditions, changes.preconditions),
        steps=content.steps if changes.steps is None else changes.steps,
        criterion_ids=content.criterion_ids if changes.criterion_ids is None else changes.criterion_ids,
        parameters=content.parameters if changes.parameters is None else changes.parameters,
        data_rows=content.data_rows if changes.data_rows is None else changes.data_rows,
    )
