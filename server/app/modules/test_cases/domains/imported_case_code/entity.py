from app.shared.common import Entity


class ImportedCaseCode(Entity):
    code: str
    story_key: str
    title: str
