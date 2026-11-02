from urllib.parse import quote

from app.modules.notifications.domains.notification_email_recipient.entity import NotificationEmailRecipient
from app.modules.notifications.domains.notification_email_texts.entity import NotificationEmailTexts
from app.modules.notifications.domains.notification_payload.entity import (
    FailureAssignedPayload,
    GapAssignedPayload,
    NotificationPayload,
    ReportReadyPayload,
    RunFinishedPayload,
    SuiteRunFinishedPayload,
)
from app.modules.notifications.typing.constants import (
    EMAIL_SUBJECT_TEMPLATE,
    NOTIFICATION_EMAIL_TEXTS,
    PROFILE_PATH,
    REPORT_SOURCE_PATHS,
)
from app.shared.mailer import EmailMessage


def build_notification_email(
    recipient: NotificationEmailRecipient, payload: NotificationPayload, client_url: str
) -> EmailMessage:
    texts = NOTIFICATION_EMAIL_TEXTS[recipient.language]
    base_url = client_url.rstrip("/")
    project_url = f"{base_url}/projects/{quote(recipient.project_key, safe='')}"
    title, detail, target_url = describe_payload(texts, payload, project_url)
    lines = [
        texts.greeting.format(name=recipient.name),
        "",
        title,
        detail,
        "",
        texts.project_line.format(project_name=recipient.project_name, project_key=recipient.project_key),
        texts.open_line.format(url=target_url),
        "",
        "--",
        texts.footer.format(settings_url=f"{base_url}{PROFILE_PATH}"),
    ]
    return EmailMessage(
        recipient=recipient.email,
        subject=" ".join(EMAIL_SUBJECT_TEMPLATE.format(project_key=recipient.project_key, title=title).split()),
        text="\n".join(lines) + "\n",
    )


def describe_payload(
    texts: NotificationEmailTexts, payload: NotificationPayload, project_url: str
) -> tuple[str, str, str]:
    match payload:
        case GapAssignedPayload():
            return (
                texts.gap_assigned_title.format(story_key=payload.story_jira_key),
                payload.question,
                f"{project_url}/stories/{quote(payload.story_jira_key, safe='')}?tab=gaps",
            )
        case FailureAssignedPayload():
            return (
                texts.failure_assigned_title.format(story_key=payload.story_jira_key),
                f"{payload.test_case_code} · {payload.test_case_title}",
                f"{project_url}/failures/{payload.failure_id}",
            )
        case RunFinishedPayload():
            return (
                texts.run_finished_titles[payload.outcome].format(story_key=payload.story_jira_key),
                format_run_counts(texts, payload.passed_count, payload.failed_count, payload.blocked_count),
                f"{project_url}/runs/{payload.run_id}",
            )
        case SuiteRunFinishedPayload():
            return (
                texts.suite_run_finished_titles[payload.outcome].format(suite_name=payload.test_suite_name),
                format_run_counts(texts, payload.passed_count, payload.failed_count, payload.blocked_count),
                f"{project_url}/runs/{payload.run_id}",
            )
        case ReportReadyPayload():
            return (
                texts.report_ready_title.format(source_label=payload.source_label),
                payload.file_name,
                f"{project_url}/{REPORT_SOURCE_PATHS[payload.source]}/{quote(payload.source_id, safe='')}",
            )


def format_run_counts(texts: NotificationEmailTexts, passed: int, failed: int, blocked: int) -> str:
    return texts.run_counts.format(passed=passed, failed=failed, blocked=blocked)
