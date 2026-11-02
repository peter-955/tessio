from app.modules.notifications import ReportFormat

CONTENT_TYPE_BY_FORMAT = {ReportFormat.MARKDOWN: "text/markdown; charset=utf-8", ReportFormat.PDF: "application/pdf"}
MAX_FILE_NAME_STEM_LENGTH = 80
EMPTY_CELL = "—"
MAX_STORY_REPORT_RUNS = 20
