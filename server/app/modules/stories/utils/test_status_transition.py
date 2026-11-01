from app.modules.stories.typing.constants import CAPABILITY_BY_TARGET_STATUS, TEST_STATUS_TRANSITIONS
from app.modules.stories.typing.enums import TestStatus
from app.shared.permissions import Capability, ProjectAccess, has_capability


def find_required_capability(target: TestStatus) -> Capability | None:
    return CAPABILITY_BY_TARGET_STATUS.get(target)


def list_available_test_statuses(access: ProjectAccess, current: TestStatus) -> frozenset[TestStatus]:
    available_statuses: set[TestStatus] = set()
    for target in TEST_STATUS_TRANSITIONS[current]:
        required_capability = find_required_capability(target)
        if required_capability is not None and has_capability(access, required_capability):
            available_statuses.add(target)
    return frozenset(available_statuses)
