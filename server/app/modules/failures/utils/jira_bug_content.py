import re

from app.modules.failures.domains.failed_step.entity import FailedStep
from app.modules.failures.domains.jira_bug_content.entity import JiraBugContent
from app.modules.failures.domains.jira_bug_source.entity import JiraBugSource
from app.modules.failures.typing.constants import (
    JIRA_BUG_LINK_TEXT,
    PARAMETER_PLACEHOLDER_PATTERN,
    TESSIO_FAILURE_URL_TEMPLATE,
)
from app.modules.jira import JiraDocumentBlock, JiraDocumentBlockKind, clean_jira_summary
from app.shared.masking import SecretMasker


def build_jira_bug_content(
    source: JiraBugSource,
    jira_project_key: str,
    failed_step: FailedStep | None,
    client_url: str,
    masker: SecretMasker,
) -> JiraBugContent:
    return JiraBugContent(
        jira_project_key=jira_project_key,
        issue_type_name=source.jira_bug_issue_type,
        summary=clean_jira_summary(masker.mask(_build_summary(source, failed_step))),
        description=[
            block.model_copy(update={"texts": [masker.mask(text) for text in block.texts]})
            for block in _build_description(source, failed_step, client_url)
        ],
        linked_story_jira_key=source.story_jira_key if source.is_story_from_jira else None,
        screenshot_file_id=None if failed_step is None else failed_step.screenshot_file_id,
    )


def _build_summary(source: JiraBugSource, failed_step: FailedStep | None) -> str:
    if failed_step is None:
        return f"{source.test_case_code} {source.test_case_title} failed"
    return f"{source.test_case_code} {source.test_case_title}: step {failed_step.step_order} failed"


def _build_description(
    source: JiraBugSource, failed_step: FailedStep | None, client_url: str
) -> list[JiraDocumentBlock]:
    blocks = [
        _paragraph(
            f"Found by Tessio while testing {source.story_jira_key} {source.story_title}, "
            f"case {source.test_case_code} {source.test_case_title}."
        )
    ]
    if source.data_row:
        blocks.extend(
            [
                _heading(f"Test data (iteration {source.iteration + 1})"),
                _block(
                    JiraDocumentBlockKind.BULLET_LIST,
                    [f"{name} = {value}" for name, value in source.data_row.items()],
                ),
            ]
        )
    if source.preconditions:
        blocks.extend([_heading("Preconditions"), _paragraph(_fill_parameters(source.preconditions, source))])
    repro_steps = _list_repro_steps(source, failed_step)
    if repro_steps:
        blocks.extend([_heading("Steps to reproduce"), _block(JiraDocumentBlockKind.ORDERED_LIST, repro_steps)])
    expected = _find_expected_result(source, failed_step)
    if expected:
        blocks.extend([_heading("Expected result"), _paragraph(expected)])
    if failed_step is not None:
        blocks.append(_heading(f"Actual result (step {failed_step.step_order})"))
        blocks.append(_paragraph(failed_step.actual_result or "No actual result was recorded."))
        if failed_step.error:
            blocks.append(_block(JiraDocumentBlockKind.CODE, [failed_step.error]))
    blocks.extend([_heading("Environment"), _paragraph(f"{source.environment_name} ({source.environment_base_url})")])
    if source.cause is not None:
        cause_label = source.cause.value.replace("_", " ").capitalize()
        reason = f": {source.cause_reason}" if source.cause_reason else ""
        blocks.extend([_heading("Suspected cause"), _paragraph(f"{cause_label}{reason}")])
    failure_url = TESSIO_FAILURE_URL_TEMPLATE.format(
        client_url=client_url.rstrip("/"), project_key=source.project_key, failure_id=source.failure_id
    )
    blocks.append(JiraDocumentBlock(kind=JiraDocumentBlockKind.LINK, texts=[JIRA_BUG_LINK_TEXT], link_url=failure_url))
    return blocks


def _list_repro_steps(source: JiraBugSource, failed_step: FailedStep | None) -> list[str]:
    if source.repro_steps:
        return [step for step in source.repro_steps if step.strip()]
    last_order = None if failed_step is None else failed_step.step_order
    return [
        _fill_parameters(step.action, source)
        for step in source.steps
        if step.action and (last_order is None or step.order <= last_order)
    ]


def _find_expected_result(source: JiraBugSource, failed_step: FailedStep | None) -> str | None:
    if failed_step is None:
        return None
    expected = next((step.expected for step in source.steps if step.order == failed_step.step_order), None)
    return None if expected is None else _fill_parameters(expected, source)


def _fill_parameters(text: str, source: JiraBugSource) -> str:
    row = source.data_row
    if not row:
        return text
    return re.sub(PARAMETER_PLACEHOLDER_PATTERN, lambda match: row.get(match.group(1), match.group(0)), text)


def _heading(text: str) -> JiraDocumentBlock:
    return _block(JiraDocumentBlockKind.HEADING, [text])


def _paragraph(text: str) -> JiraDocumentBlock:
    return _block(JiraDocumentBlockKind.PARAGRAPH, [text])


def _block(kind: JiraDocumentBlockKind, texts: list[str]) -> JiraDocumentBlock:
    return JiraDocumentBlock(kind=kind, texts=texts)
