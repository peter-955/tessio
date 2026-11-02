from app.modules.reports import PdfRenderer

FAKE_PDF_PREFIX = b"%PDF-1.7 fake\n"


class RecordingPdfRenderer(PdfRenderer):
    def __init__(self) -> None:
        self.html_pages: list[str] = []

    async def render(self, html: str) -> bytes:
        self.html_pages.append(html)
        return FAKE_PDF_PREFIX + html.encode()
