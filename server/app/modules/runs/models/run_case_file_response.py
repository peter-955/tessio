from app.shared.common import WireModel


class RunCaseFileResponse(WireModel):
    key: str
    file_name: str
