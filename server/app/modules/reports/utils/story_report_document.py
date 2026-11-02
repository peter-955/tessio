from datetime import datetime

from app.modules.insights import Traceability
from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.typing.enums import ReportText
from app.modules.reports.utils.report_text import format_moment, format_optional, label_value, translate
from app.modules.reports.utils.table_section import build_table_section
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.users import UserLanguage


def build_story_document(
    traceability: Traceability, runs: list[RunSummary], language: UserLanguage, generated_at: datetime
) -> ReportDocument:
    story = traceability.story
    coverage = traceability.coverage
    cases_by_id = {case.id: case for case in traceability.cases}
    facts = [
        ReportFact(label=translate(language, ReportText.TEST_STATUS), value=label_value(language, story.test_status)),
        ReportFact(
            label=translate(language, ReportText.COVERAGE),
            value=translate(language, ReportText.COVERAGE_SUMMARY).format(
                covered=coverage.covered_count, total=coverage.criterion_count, passed=coverage.passed_count
            ),
        ),
        ReportFact(label=translate(language, ReportText.GENERATED_AT), value=format_moment(generated_at)),
    ]
    criteria_rows = [
        [
            trace.criterion.code,
            trace.criterion.text,
            label_value(language, trace.status),
            ", ".join(cases_by_id[case_id].code for case_id in trace.linked_case_ids if case_id in cases_by_id)
            or format_optional(None),
        ]
        for trace in traceability.criteria
        if trace.criterion.is_active
    ]
    case_rows = [
        [
            case.code,
            case.title,
            label_value(language, case.status),
            label_value(language, case.priority),
            translate(language, ReportText.NOT_RUN)
            if case.latest_result is None
            else label_value(language, case.latest_result.status),
            ", ".join(
                translate(language, key)
                for key, is_set in ((ReportText.FLAKY, case.is_flaky), (ReportText.QUARANTINED, case.is_quarantined))
                if is_set
            )
            or format_optional(None),
        ]
        for case in traceability.cases
    ]
    run_rows = [
        [
            format_moment(summary.run.started_at),
            label_value(language, summary.run.executor),
            label_value(language, summary.run.status),
            summary.labels.environment_name,
            str(summary.counts.passed),
            str(summary.counts.failed),
            str(summary.counts.blocked),
            str(summary.counts.not_reported),
        ]
        for summary in runs
    ]
    return ReportDocument(
        title=f"{translate(language, ReportText.STORY_TITLE)} · {story.jira_key} {story.title}",
        subtitle=story.jira_key,
        facts=facts,
        sections=[
            build_table_section(
                translate(language, ReportText.ACCEPTANCE_CRITERIA),
                [
                    translate(language, key)
                    for key in (ReportText.CRITERION, ReportText.TEXT, ReportText.STATUS, ReportText.LINKED_CASES)
                ],
                criteria_rows,
                language,
            ),
            build_table_section(
                translate(language, ReportText.CASES),
                [
                    translate(language, key)
                    for key in (
                        ReportText.CASE,
                        ReportText.TITLE,
                        ReportText.STATUS,
                        ReportText.PRIORITY,
                        ReportText.LATEST_RESULT,
                        ReportText.FLAGS,
                    )
                ],
                case_rows,
                language,
            ),
            build_table_section(
                translate(language, ReportText.RUNS),
                [
                    translate(language, key)
                    for key in (
                        ReportText.STARTED_AT,
                        ReportText.EXECUTOR,
                        ReportText.STATUS,
                        ReportText.ENVIRONMENT,
                        ReportText.PASSED,
                        ReportText.FAILED,
                        ReportText.BLOCKED,
                        ReportText.NOT_REPORTED,
                    )
                ],
                run_rows,
                language,
            ),
        ],
    )
