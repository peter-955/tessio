from app.modules.jira import JiraCommentTrigger, JiraDocumentBlock, JiraDocumentBlockKind
from app.modules.runs.domains.jira_comment_source.entity import JiraCommentSource
from app.modules.runs.typing.constants.jira_comment import (
    JIRA_COMMENT_LINK_TEXT,
    TESSIO_RUN_URL_TEMPLATE,
    TESSIO_STORY_URL_TEMPLATE,
)


def build_jira_result_comment(
    source: JiraCommentSource, trigger: JiraCommentTrigger, client_url: str
) -> list[JiraDocumentBlock]:
    base_url = client_url.rstrip("/")
    if trigger is JiraCommentTrigger.SIGN_OFF:
        headline = f"Tessio: {source.story_jira_key} was signed off."
        link_url = TESSIO_STORY_URL_TEMPLATE.format(
            client_url=base_url, project_key=source.project_key, jira_key=source.story_jira_key
        )
    else:
        status = "unknown" if source.run_status is None else source.run_status.value
        headline = f"Tessio: a test run finished ({status})."
        link_url = TESSIO_RUN_URL_TEMPLATE.format(
            client_url=base_url, project_key=source.project_key, run_id=source.run_id
        )
    return [
        JiraDocumentBlock(kind=JiraDocumentBlockKind.PARAGRAPH, texts=[headline]),
        JiraDocumentBlock(kind=JiraDocumentBlockKind.BULLET_LIST, texts=_build_count_lines(source)),
        JiraDocumentBlock(kind=JiraDocumentBlockKind.LINK, texts=[JIRA_COMMENT_LINK_TEXT], link_url=link_url),
    ]


def _build_count_lines(source: JiraCommentSource) -> list[str]:
    lines: list[str] = []
    counts = source.counts
    if counts is None:
        lines.append("No results recorded yet.")
    else:
        lines.extend(
            [
                f"Passed: {counts.passed} of {counts.total}",
                f"Failed: {counts.failed}",
                f"Blocked: {counts.blocked}",
                f"Skipped: {counts.skipped}",
                f"Not reported: {counts.not_reported}",
            ]
        )
    if source.environment_name is not None:
        lines.append(f"Environment: {source.environment_name}")
    return lines
