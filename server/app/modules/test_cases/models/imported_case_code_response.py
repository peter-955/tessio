from app.shared.common import WireModel


class ImportedCaseCodeResponse(WireModel):
    code: str
    story_key: str
    title: str
