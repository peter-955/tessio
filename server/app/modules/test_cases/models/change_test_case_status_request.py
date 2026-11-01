from app.modules.test_cases.typing.enums import TestCaseStatus
from app.shared.common import WireModel


class ChangeTestCaseStatusRequest(WireModel):
    status: TestCaseStatus
