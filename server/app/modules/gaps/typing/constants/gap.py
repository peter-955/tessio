from collections.abc import Mapping

from app.modules.gaps.typing.enums import GapSeverity, GapType
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
MAX_MY_GAPS = 50
MAX_SIMILAR_ANSWERS = 3
TEST_DATA_PAGE_PATH = "/projects/{project_key}/test-data"
MAX_SEARCH_TERMS = 20
MIN_SEARCH_TERM_LENGTH = 3
SEARCH_CONFIGURATION = "simple"
SEARCH_VECTOR_EXPRESSION = "to_tsvector('simple'::regconfig, question || ' ' || coalesce(answer, ''))"
SEARCH_TERM_PATTERN = r"\w+"
SEARCH_TERM_SEPARATOR = " or "
SEARCH_STOP_WORDS = frozenset(
    {
        "about",
        "and",
        "are",
        "can",
        "does",
        "for",
        "from",
        "has",
        "have",
        "how",
        "into",
        "not",
        "or",
        "should",
        "that",
        "the",
        "their",
        "there",
        "this",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "you",
        "your",
    }
)
SEVERITY_RANK: Mapping[GapSeverity, int] = {GapSeverity.HIGH: 0, GapSeverity.MEDIUM: 1, GapSeverity.LOW: 2}
