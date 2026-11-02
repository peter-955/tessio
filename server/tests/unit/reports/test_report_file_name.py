from app.modules.notifications import ReportFormat
from app.modules.reports.utils.report_file_name import build_report_file_name


def test_file_names_are_ascii_and_safe() -> None:
    assert build_report_file_name("plan-Release 3.0", ReportFormat.MARKDOWN) == "plan-Release-3.0.md"
    assert build_report_file_name("run-Kiểm thử/Thanh toán", ReportFormat.PDF) == "run-Kiem-thu-Thanh-toan.pdf"
    assert build_report_file_name("../../etc", ReportFormat.PDF) == "etc.pdf"
    assert build_report_file_name("你好", ReportFormat.PDF) == "report.pdf"
    assert len(build_report_file_name("x" * 300, ReportFormat.MARKDOWN)) == 83
