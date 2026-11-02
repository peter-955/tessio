from uuid import uuid7

from app.modules.failures.domains.failed_step.entity import FailedStep
from app.modules.failures.domains.jira_bug_source.entity import JiraBugSource
from app.modules.failures.utils.jira_bug_content import build_jira_bug_content
from app.modules.jira import JiraDocumentBlockKind, render_jira_document_text
from app.modules.runs import SuspectedCause
from app.modules.test_cases import TestStep as CaseStep
from app.shared.masking import MASKED_VALUE, SecretMasker

FAILURE_ID = uuid7()
SCREENSHOT_ID = uuid7()


def build_source(**changes: object) -> JiraBugSource:
    source = JiraBugSource(
        failure_id=FAILURE_ID,
        project_key="SHOP",
        jira_project_key="PAY",
        jira_bug_issue_type="Bug",
        story_jira_key="PAY-7",
        story_title="Pay by card",
        is_story_from_jira=True,
        test_case_code="TC-4",
        test_case_title="Card payment",
        preconditions=None,
        steps=[
            CaseStep(order=1, action="Open the cart", expected="One item"),
            CaseStep(order=2, action="Pay with card 4242", expected="Payment accepted"),
            CaseStep(order=3, action="Open the receipt", expected="Total shown"),
        ],
        iteration=0,
        data_row=None,
        repro_steps=None,
        environment_id=uuid7(),
        environment_name="Staging",
        environment_base_url="https://staging.shop.test",
        cause=SuspectedCause.APP_BUG,
        cause_reason="The gateway returns 500",
    )
    return source.model_copy(update=changes)


FAILED_STEP = FailedStep(
    step_order=2,
    actual_result="Declined for card 4242",
    error="HTTP 500",
    screenshot_file_id=SCREENSHOT_ID,
    diagnosis=None,
)


def test_the_bug_lists_the_steps_up_to_the_failing_step_and_the_evidence() -> None:
    content = build_jira_bug_content(build_source(), "PAY", FAILED_STEP, "https://tessio.test/", SecretMasker([]))

    assert content.summary == "TC-4 Card payment: step 2 failed"
    assert content.issue_type_name == "Bug"
    assert content.linked_story_jira_key == "PAY-7"
    assert content.screenshot_file_id == SCREENSHOT_ID
    text = render_jira_document_text(content.description)
    assert "Steps to reproduce\n\n1. Open the cart\n2. Pay with card 4242" in text
    assert "Open the receipt" not in text
    assert "Expected result\n\nPayment accepted" in text
    assert "Actual result (step 2)\n\nDeclined for card 4242\n\nHTTP 500" in text
    assert "Environment\n\nStaging (https://staging.shop.test)" in text
    assert "Suspected cause\n\nApp bug: The gateway returns 500" in text
    assert text.endswith(f"Open the failure in Tessio: https://tessio.test/projects/SHOP/failures/{FAILURE_ID}")
    assert [block.kind for block in content.description].count(JiraDocumentBlockKind.CODE) == 1


def test_recorded_repro_steps_replace_the_case_steps() -> None:
    source = build_source(repro_steps=["Go to /cart", "  ", "Click Pay"])

    content = build_jira_bug_content(source, "PAY", FAILED_STEP, "https://tessio.test", SecretMasker([]))

    text = render_jira_document_text(content.description)
    assert "Steps to reproduce\n\n1. Go to /cart\n2. Click Pay\n\n" in text
    assert "Open the cart" not in text


def test_secrets_are_masked_in_the_summary_and_description() -> None:
    content = build_jira_bug_content(
        build_source(test_case_title="Pay with 4242"), "PAY", FAILED_STEP, "https://tessio.test", SecretMasker(["4242"])
    )

    text = render_jira_document_text(content.description)
    assert "4242" not in content.summary
    assert "4242" not in text
    assert MASKED_VALUE in text


def test_a_case_without_a_failing_step_or_cause_still_makes_a_bug() -> None:
    source = build_source(cause=None, cause_reason=None, is_story_from_jira=False, preconditions="Signed in")

    content = build_jira_bug_content(source, "PAY", None, "https://tessio.test", SecretMasker([]))

    text = render_jira_document_text(content.description)
    assert content.summary == "TC-4 Card payment failed"
    assert content.linked_story_jira_key is None
    assert content.screenshot_file_id is None
    assert "Preconditions\n\nSigned in" in text
    assert "Open the receipt" in text
    assert "Suspected cause" not in text
    assert "Actual result" not in text
    assert "Test data" not in text


def test_a_data_driven_failure_fills_in_the_failing_row_and_lists_its_values() -> None:
    source = build_source(
        preconditions="Signed in as {{param.user}}",
        steps=[
            CaseStep(order=1, action="Open the cart", expected="One item"),
            CaseStep(order=2, action="Pay with card {{ param.card }}", expected="Payment {{param.outcome}}"),
            CaseStep(order=3, action="Open the receipt", expected="Total shown"),
        ],
        iteration=2,
        data_row={"user": "{{data.shopper}}", "card": "4000 0002", "outcome": "declined"},
    )

    content = build_jira_bug_content(source, "PAY", FAILED_STEP, "https://tessio.test", SecretMasker(["4000 0002"]))

    text = render_jira_document_text(content.description)
    test_data = (
        f"Test data (iteration 3)\n\n- user = {{{{data.shopper}}}}\n- card = {MASKED_VALUE}\n- outcome = declined"
    )
    assert test_data in text
    assert "Preconditions\n\nSigned in as {{data.shopper}}" in text
    assert f"Steps to reproduce\n\n1. Open the cart\n2. Pay with card {MASKED_VALUE}\n\n" in text
    assert "Expected result\n\nPayment declined" in text
    assert "param." not in text
    assert "4000 0002" not in text


def test_a_placeholder_without_a_value_in_the_row_is_kept() -> None:
    source = build_source(
        steps=[CaseStep(order=1, action="Pay with {{param.card}} and {{param.coupon}}", expected="Paid")],
        data_row={"card": "4242"},
    )

    content = build_jira_bug_content(
        source, "PAY", FAILED_STEP.model_copy(update={"step_order": 1}), "https://tessio.test", SecretMasker([])
    )

    assert "1. Pay with 4242 and {{param.coupon}}" in render_jira_document_text(content.description)
