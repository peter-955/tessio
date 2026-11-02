from datetime import UTC, datetime
from uuid import uuid7

import pytest
from annotated_types import MaxLen

from app.modules.runs.models.manual_case_result_request import ManualCaseResultRequest
from app.modules.runs.typing.constants.run import MAX_STEPS_PER_CASE
from app.modules.shared_steps import (
    MAX_EXPANDED_CASE_STEPS,
    CurrentSharedStep,
    SharedStep,
    SharedStepAction,
    SharedStepVersion,
    UnknownSharedStepError,
    count_expanded_steps,
)
from app.modules.test_cases import TestStep as CaseStep
from app.modules.test_cases.utils.shared_step_expansion import expand_steps


def build_current(key: str, actions: list[str], number: int = 1) -> CurrentSharedStep:
    now = datetime.now(UTC)
    shared_step_id = uuid7()
    version = SharedStepVersion(
        id=uuid7(),
        shared_step_id=shared_step_id,
        number=number,
        steps=[SharedStepAction(order=order, action=action, expected=None) for order, action in enumerate(actions, 1)],
        data_keys=[],
        created_by=uuid7(),
        created_at=now,
    )
    shared_step = SharedStep(
        id=shared_step_id,
        project_id=uuid7(),
        key=key,
        title=key,
        current_version_id=version.id,
        archived_at=None,
        created_by=uuid7(),
        created_at=now,
    )
    return CurrentSharedStep(shared_step=shared_step, version=version)


def test_shared_steps_are_expanded_in_place_and_every_step_is_renumbered() -> None:
    shared_steps = {
        "log_in": build_current("log_in", ["Open sign-in", "Sign in"], number=3),
        "log_out": build_current("log_out", ["Sign out"]),
    }
    steps = [
        CaseStep(order=1, shared_step_key="log_in"),
        CaseStep(order=2, action="Pay", expected="Paid"),
        CaseStep(order=3, shared_step_key="log_out"),
        CaseStep(order=4, shared_step_key="log_in"),
    ]

    expanded = expand_steps(steps, shared_steps)

    assert [(step.order, step.action, step.shared_step_key, step.shared_step_version_number) for step in expanded] == [
        (1, "Open sign-in", "log_in", 3),
        (2, "Sign in", "log_in", 3),
        (3, "Pay", None, None),
        (4, "Sign out", "log_out", 1),
        (5, "Open sign-in", "log_in", 3),
        (6, "Sign in", "log_in", 3),
    ]


def test_a_missing_shared_step_cannot_be_expanded() -> None:
    with pytest.raises(UnknownSharedStepError):
        expand_steps([CaseStep(order=1, shared_step_key="gone")], {})


def test_a_reference_step_is_stored_without_empty_fields() -> None:
    assert CaseStep(order=2, shared_step_key="log_in").model_dump() == {"order": 2, "shared_step_key": "log_in"}
    assert CaseStep(order=1, action="Pay").model_dump() == {"order": 1, "action": "Pay", "expected": None}


def test_a_shared_step_counts_as_its_actions_and_a_plain_step_as_one() -> None:
    assert count_expanded_steps([None, "log_in", None, "log_in"], {"log_in": 3}) == 8


def test_the_expanded_step_limit_matches_what_a_result_can_report() -> None:
    manual_limits = [
        item.max_length for item in ManualCaseResultRequest.model_fields["steps"].metadata if isinstance(item, MaxLen)
    ]

    assert MAX_EXPANDED_CASE_STEPS == MAX_STEPS_PER_CASE
    assert manual_limits == [MAX_EXPANDED_CASE_STEPS]
