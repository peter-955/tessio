from app.modules.test_data.typing.enums import ImportSkipReason
from app.shared.common import Entity


class ImportSkip(Entity):
    location: str
    reason: ImportSkipReason
