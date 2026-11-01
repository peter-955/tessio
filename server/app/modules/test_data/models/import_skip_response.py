from app.modules.test_data.typing.enums import ImportSkipReason
from app.shared.common import WireModel


class ImportSkipResponse(WireModel):
    location: str
    reason: ImportSkipReason
