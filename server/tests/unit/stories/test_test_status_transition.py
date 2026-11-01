from collections.abc import Mapping
from uuid import uuid7

import pytest

from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.utils.test_status_transition import find_required_capability, list_available_test_statuses
from app.shared.permissions import Capability, ProjectAccess, ProjectRole

NOT_STARTED = StoryTestStatus.NOT_STARTED
READY_FOR_TEST = StoryTestStatus.READY_FOR_TEST
IN_TEST = StoryTestStatus.IN_TEST
PASSED = StoryTestStatus.PASSED
FAILED = StoryTestStatus.FAILED

NO_TARGETS: Mapping[StoryTestStatus, set[StoryTestStatus]] = {status: set() for status in StoryTestStatus}

EXPECTED_TARGETS_BY_ROLE: Mapping[ProjectRole, Mapping[StoryTestStatus, set[StoryTestStatus]]] = {
    ProjectRole.ADMIN: {
        NOT_STARTED: {READY_FOR_TEST},
        READY_FOR_TEST: {NOT_STARTED},
        IN_TEST: {PASSED, FAILED},
        PASSED: {FAILED},
        FAILED: {PASSED, READY_FOR_TEST},
    },
    ProjectRole.DEV: {
        NOT_STARTED: {READY_FOR_TEST},
        READY_FOR_TEST: {NOT_STARTED},
        IN_TEST: set(),
        PASSED: set(),
        FAILED: {READY_FOR_TEST},
    },
    ProjectRole.QC: {
        NOT_STARTED: set(),
        READY_FOR_TEST: set(),
        IN_TEST: {PASSED, FAILED},
        PASSED: {FAILED},
        FAILED: {PASSED},
    },
    ProjectRole.PM: NO_TARGETS,
    ProjectRole.BA: NO_TARGETS,
    ProjectRole.VIEWER: NO_TARGETS,
}


def build_access(role: ProjectRole | None, is_archived: bool = False) -> ProjectAccess:
    return ProjectAccess(project_id=uuid7(), project_key="SHOP", role=role, is_archived=is_archived)


@pytest.mark.parametrize("target", list(StoryTestStatus))
@pytest.mark.parametrize("current", list(StoryTestStatus))
@pytest.mark.parametrize("role", list(ProjectRole))
def test_every_role_and_status_pair_matches_the_table(
    role: ProjectRole, current: StoryTestStatus, target: StoryTestStatus
) -> None:
    available = list_available_test_statuses(build_access(role), current)

    assert (target in available) is (target in EXPECTED_TARGETS_BY_ROLE[role][current])


@pytest.mark.parametrize("current", list(StoryTestStatus))
@pytest.mark.parametrize("role", list(ProjectRole))
def test_an_archived_project_offers_nothing(role: ProjectRole, current: StoryTestStatus) -> None:
    assert list_available_test_statuses(build_access(role, is_archived=True), current) == frozenset()


@pytest.mark.parametrize("current", list(StoryTestStatus))
def test_a_non_member_is_offered_nothing(current: StoryTestStatus) -> None:
    assert list_available_test_statuses(build_access(None), current) == frozenset()


@pytest.mark.parametrize(
    ("target", "expected_capability"),
    [
        (NOT_STARTED, Capability.STORY_MARK_READY_FOR_TEST),
        (READY_FOR_TEST, Capability.STORY_MARK_READY_FOR_TEST),
        (IN_TEST, None),
        (PASSED, Capability.STORY_SIGN_OFF),
        (FAILED, Capability.STORY_SIGN_OFF),
    ],
)
def test_each_target_needs_its_capability(target: StoryTestStatus, expected_capability: Capability | None) -> None:
    assert find_required_capability(target) is expected_capability
