from app.modules.reports import ReportFileWriter


class InMemoryReportFileWriter(ReportFileWriter):
    def __init__(self) -> None:
        self.files: dict[str, tuple[bytes, str]] = {}

    async def write(self, key: str, content: bytes, content_type: str) -> None:
        self.files[key] = (content, content_type)
