from collections.abc import Mapping

from app.modules.gaps.typing.enums import GapType
from app.shared.permissions import ProjectRole

ROUTED_ROLE_BY_GAP_TYPE: Mapping[GapType, ProjectRole] = {
    GapType.MISSING_ACCEPTANCE_CRITERIA: ProjectRole.BA,
    GapType.UNCLEAR_GOAL: ProjectRole.BA,
    GapType.MISSING_STEP: ProjectRole.QC,
    GapType.MISSING_TEST_DATA: ProjectRole.QC,
    GapType.OTHER: ProjectRole.ADMIN,
}
ENVIRONMENT_DATA_ROLE = ProjectRole.DEV
FALLBACK_ROLE = ProjectRole.ADMIN
REOPENING_ROLES = frozenset({ProjectRole.QC, ProjectRole.ADMIN})
MAX_QUESTION_LENGTH = 2000
MAX_ANSWER_LENGTH = 4000
MAX_TARGET_REF_LENGTH = 40
MAX_GAPS_PER_CALL = 50
MAX_INBOX_SIZE = 200
TEST_CASE_CODE_PREFIX = "TC-"
TEST_CASE_CODE_PATTERN = r"(?i)^TC-([1-9][0-9]{0,8})$"
