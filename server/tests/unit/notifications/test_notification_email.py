from uuid import UUID

import pytest

from app.modules.notifications import (
    FailureAssignedPayload,
    GapAssignedPayload,
    NotificationPayload,
    RunFinishedPayload,
    RunOutcome,
    SuiteRunFinishedPayload,
)
from app.modules.notifications.domains.notification_email_recipient.entity import NotificationEmailRecipient
from app.modules.notifications.domains.notification_payload.entity import ReportReadyPayload
from app.modules.notifications.typing.enums import ReportFormat, ReportSource
from app.modules.notifications.utils.notification_email import build_notification_email
from app.modules.users import UserLanguage

CLIENT_URL = "https://tessio.test/"
GAP_ID = UUID("01900000-0000-7000-8000-000000000001")
FAILURE_ID = UUID("01900000-0000-7000-8000-000000000002")
RUN_ID = UUID("01900000-0000-7000-8000-000000000003")
OTHER_ID = UUID("01900000-0000-7000-8000-000000000004")


def build_recipient(language: UserLanguage) -> NotificationEmailRecipient:
    return NotificationEmailRecipient(
        email="olivia@tessio.test", name="Olivia", language=language, project_key="SHOP", project_name="Shop"
    )


def build_gap_payload() -> GapAssignedPayload:
    return GapAssignedPayload(
        gap_id=GAP_ID, story_id=OTHER_ID, story_jira_key="SHOP-12", question="Which currencies does checkout accept?"
    )


def build_failure_payload() -> FailureAssignedPayload:
    return FailureAssignedPayload(
        failure_id=FAILURE_ID,
        test_case_id=OTHER_ID,
        test_case_code="TC-7",
        test_case_title="Pay with a saved card",
        story_jira_key="SHOP-12",
    )


def build_run_payload(outcome: RunOutcome) -> RunFinishedPayload:
    return RunFinishedPayload(
        run_id=RUN_ID,
        story_id=OTHER_ID,
        story_jira_key="SHOP-12",
        outcome=outcome,
        passed_count=8,
        failed_count=1,
        blocked_count=2,
    )


@pytest.mark.parametrize(
    ("language", "subject", "greeting", "footer_start"),
    [
        (UserLanguage.EN, "[SHOP] Gap assigned to you on SHOP-12", "Hello Olivia,", "You get this email"),
        (
            UserLanguage.FR,
            "[SHOP] Écart qui vous est attribué sur SHOP-12",
            "Bonjour Olivia,",
            "Vous recevez cet e-mail",
        ),
        (
            UserLanguage.VI,
            "[SHOP] Khoảng trống được giao cho bạn ở SHOP-12",
            "Xin chào Olivia,",
            "Bạn nhận được email này",
        ),
    ],
)
def test_a_gap_email_is_written_in_the_recipients_language(
    language: UserLanguage, subject: str, greeting: str, footer_start: str
) -> None:
    message = build_notification_email(build_recipient(language), build_gap_payload(), CLIENT_URL)

    lines = message.text.splitlines()
    assert message.recipient == "olivia@tessio.test"
    assert message.subject == subject
    assert lines[0] == greeting
    assert lines[2] == subject.removeprefix("[SHOP] ")
    assert lines[3] == "Which currencies does checkout accept?"
    assert "https://tessio.test/projects/SHOP/stories/SHOP-12?tab=gaps" in lines[6]
    assert lines[-1].startswith(footer_start)
    assert lines[-1].endswith("https://tessio.test/profile")


@pytest.mark.parametrize(
    ("language", "title"),
    [
        (UserLanguage.EN, "Failure assigned to you on SHOP-12"),
        (UserLanguage.FR, "Échec qui vous est attribué sur SHOP-12"),
        (UserLanguage.VI, "Lỗi được giao cho bạn ở SHOP-12"),
    ],
)
def test_a_failure_email_names_the_case_and_links_the_failure(language: UserLanguage, title: str) -> None:
    message = build_notification_email(build_recipient(language), build_failure_payload(), CLIENT_URL)

    assert message.subject == f"[SHOP] {title}"
    assert "TC-7 · Pay with a saved card" in message.text
    assert f"https://tessio.test/projects/SHOP/failures/{FAILURE_ID}" in message.text


@pytest.mark.parametrize(
    ("language", "outcome", "title", "counts"),
    [
        (UserLanguage.EN, RunOutcome.PASSED, "Run passed on SHOP-12", "8 passed · 1 failed · 2 blocked"),
        (UserLanguage.EN, RunOutcome.ABORTED, "Run aborted on SHOP-12", "8 passed · 1 failed · 2 blocked"),
        (UserLanguage.FR, RunOutcome.FAILED, "Exécution en échec sur SHOP-12", "8 réussis · 1 en échec · 2 bloqués"),
        (UserLanguage.VI, RunOutcome.PASSED, "Lượt chạy đạt ở SHOP-12", "8 đạt · 1 không đạt · 2 bị chặn"),
    ],
)
def test_a_run_email_gives_the_outcome_and_counts(
    language: UserLanguage, outcome: RunOutcome, title: str, counts: str
) -> None:
    message = build_notification_email(build_recipient(language), build_run_payload(outcome), CLIENT_URL)

    assert message.subject == f"[SHOP] {title}"
    assert counts in message.text
    assert f"https://tessio.test/projects/SHOP/runs/{RUN_ID}" in message.text


@pytest.mark.parametrize(
    ("language", "title"),
    [
        (UserLanguage.EN, "Suite run failed: Nightly smoke"),
        (UserLanguage.FR, "Exécution de suite en échec : Nightly smoke"),
        (UserLanguage.VI, "Lượt chạy bộ kiểm thử không đạt: Nightly smoke"),
    ],
)
def test_a_suite_run_email_names_the_suite(language: UserLanguage, title: str) -> None:
    payload = SuiteRunFinishedPayload(
        run_id=RUN_ID,
        test_suite_id=OTHER_ID,
        test_suite_name="Nightly smoke",
        outcome=RunOutcome.FAILED,
        passed_count=3,
        failed_count=1,
        blocked_count=0,
    )

    message = build_notification_email(build_recipient(language), payload, CLIENT_URL)

    assert message.subject == f"[SHOP] {title}"
    assert f"https://tessio.test/projects/SHOP/runs/{RUN_ID}" in message.text


@pytest.mark.parametrize(
    ("language", "title"),
    [
        (UserLanguage.EN, "Your report is ready: Run on SHOP-12"),
        (UserLanguage.FR, "Votre rapport est prêt : Run on SHOP-12"),
        (UserLanguage.VI, "Báo cáo của bạn đã sẵn sàng: Run on SHOP-12"),
    ],
)
def test_a_report_email_links_the_reported_page(language: UserLanguage, title: str) -> None:
    payload = ReportReadyPayload(
        file_id=OTHER_ID,
        file_name="run-report.pdf",
        format=ReportFormat.PDF,
        source=ReportSource.RUN,
        source_id=str(RUN_ID),
        source_label="Run on SHOP-12",
    )

    message = build_notification_email(build_recipient(language), payload, CLIENT_URL)

    assert message.subject == f"[SHOP] {title}"
    assert "run-report.pdf" in message.text
    assert f"https://tessio.test/projects/SHOP/runs/{RUN_ID}" in message.text


def test_line_breaks_in_a_name_never_reach_the_subject() -> None:
    payload: NotificationPayload = SuiteRunFinishedPayload(
        run_id=RUN_ID,
        test_suite_id=OTHER_ID,
        test_suite_name="Nightly\nBcc: someone@evil.test",
        outcome=RunOutcome.PASSED,
        passed_count=1,
        failed_count=0,
        blocked_count=0,
    )

    message = build_notification_email(build_recipient(UserLanguage.EN), payload, CLIENT_URL)

    assert "\n" not in message.subject
    assert message.subject == "[SHOP] Suite run passed: Nightly Bcc: someone@evil.test"
