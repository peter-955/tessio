from app.modules.test_data.domains.import_entry.entity import ImportEntry
from app.modules.test_data.domains.import_skip.entity import ImportSkip
from app.modules.test_data.typing.enums import ImportFormat
from app.shared.common import Entity


class ParsedImport(Entity):
    format: ImportFormat
    entries: list[ImportEntry]
    skipped: list[ImportSkip]
