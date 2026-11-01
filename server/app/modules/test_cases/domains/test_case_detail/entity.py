from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_file_detail.entity import TestFileDetail
from app.shared.common import Entity


class TestCaseDetail(Entity):
    test_case: TestCase
    story: CaseStory
    version: TestCaseVersion
    criteria: list[CaseCriterion]
    files: list[TestFileDetail]
    unknown_references: list[str]
