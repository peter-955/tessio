from app.modules.stories.typing.enums import TestStatus
from app.shared.common import WireModel


class ChangeTestStatusRequest(WireModel):
    test_status: TestStatus
