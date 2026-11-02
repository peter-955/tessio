from datetime import datetime

from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.domains.report_section.entity import ReportSection
from app.modules.reports.domains.report_table.entity import ReportTable
from app.modules.reports.typing.enums import ReportText
from app.modules.reports.utils.report_text import (
    format_duration,
    format_moment,
    format_optional,
    label_value,
    translate,
)
from app.modules.runs import RunReport
from app.modules.runs.domains.run_case_detail.entity import RunCaseDetail
from app.modules.runs.domains.run_detail.entity import RunDetail
from app.modules.users import UserLanguage


def describe_run_label(detail: RunDetail) -> str:
    labels = detail.labels
    if labels.test_suite_name is not None:
        return labels.test_suite_name
    if labels.story_jira_key is not None:
        return f"{labels.story_jira_key} {labels.story_title or ''}".strip()
    return str(detail.run.id)


def describe_run_file_label(detail: RunDetail) -> str:
    return detail.labels.test_suite_name or detail.labels.story_jira_key or str(detail.run.id)


def build_run_document(detail: RunDetail, language: UserLanguage, generated_at: datetime) -> ReportDocument:
    run = detail.run
    labels = detail.labels
    is_suite_run = run.test_suite_id is not None
    facts = [
        ReportFact(label=translate(language, ReportText.STATUS), value=label_value(language, run.status)),
        ReportFact(label=translate(language, ReportText.EXECUTOR), value=label_value(language, run.executor)),
        ReportFact(
            label=translate(language, ReportText.ENVIRONMENT),
            value=f"{labels.environment_name} ({labels.environment_base_url})",
        ),
        ReportFact(label=translate(language, ReportText.STARTED_BY), value=labels.started_by_name),
        ReportFact(label=translate(language, ReportText.STARTED_AT), value=format_moment(run.started_at)),
        ReportFact(label=translate(language, ReportText.FINISHED_AT), value=format_moment(run.finished_at)),
        ReportFact(
            label=translate(language, ReportText.DURATION), value=format_duration(run.started_at, run.finished_at)
        ),
    ]
    if run.abort_reason is not None:
        facts.append(
            ReportFact(
                label=translate(language, ReportText.ABORT_REASON), value=label_value(language, run.abort_reason)
            )
        )
    if run.parent_run_id is not None:
        facts.append(ReportFact(label=translate(language, ReportText.PARENT_RUN), value=str(run.parent_run_id)))
    facts.append(ReportFact(label=translate(language, ReportText.GENERATED_AT), value=format_moment(generated_at)))
    title_key = ReportText.SUITE_RUN_TITLE if is_suite_run else ReportText.RUN_TITLE
    return ReportDocument(
        title=f"{translate(language, title_key)} · {describe_run_label(detail)}",
        subtitle=str(run.id),
        facts=facts,
        sections=[
            *build_report_sections(run.report, language, is_suite_run),
            build_case_section(detail.cases, language),
        ],
    )


def build_report_sections(report: RunReport | None, language: UserLanguage, is_suite_run: bool) -> list[ReportSection]:
    if report is None:
        return [
            ReportSection(
                heading=translate(language, ReportText.RESULTS),
                paragraphs=[translate(language, ReportText.REPORT_NOT_BUILT)],
            )
        ]
    counts = report.counts
    sections = []
    if report.summary:
        sections.append(ReportSection(heading=translate(language, ReportText.SUMMARY), paragraphs=[report.summary]))
    count_headers = [
        translate(language, key)
        for key in (
            ReportText.TOTAL,
            ReportText.PASSED,
            ReportText.FAILED,
            ReportText.BLOCKED,
            ReportText.SKIPPED,
            ReportText.NOT_REPORTED,
        )
    ]
    sections.append(
        ReportSection(
            heading=translate(language, ReportText.RESULTS),
            table=ReportTable(
                headers=count_headers,
                rows=[
                    [
                        str(value)
                        for value in (
                            counts.total,
                            counts.passed,
                            counts.failed,
                            counts.blocked,
                            counts.skipped,
                            counts.not_reported,
                        )
                    ]
                ],
            ),
        )
    )
    if is_suite_run and report.stories:
        sections.append(
            ReportSection(
                heading=translate(language, ReportText.RESULTS_BY_STORY),
                table=ReportTable(
                    headers=[translate(language, ReportText.STORY), *count_headers],
                    rows=[
                        [
                            f"{story.story_jira_key} {story.story_title}",
                            *(
                                str(value)
                                for value in (
                                    story.counts.total,
                                    story.counts.passed,
                                    story.counts.failed,
                                    story.counts.blocked,
                                    story.counts.skipped,
                                    story.counts.not_reported,
                                )
                            ),
                        ]
                        for story in report.stories
                    ],
                ),
            )
        )
    sections.append(
        ReportSection(
            heading=translate(language, ReportText.FAILED_CASES),
            table=ReportTable(
                headers=[
                    translate(language, key)
                    for key in (
                        ReportText.CASE,
                        ReportText.TITLE,
                        ReportText.STORY,
                        ReportText.STATUS,
                        ReportText.FAILING_STEP,
                        ReportText.ACTUAL_RESULT,
                        ReportText.ERROR,
                        ReportText.SUSPECTED_CAUSE,
                    )
                ],
                rows=[
                    [
                        failed_case.code,
                        failed_case.title,
                        format_optional(failed_case.story_jira_key),
                        label_value(language, failed_case.status),
                        format_optional(
                            None
                            if failed_case.step_order is None
                            else f"{failed_case.step_order}. {failed_case.step_action or ''}".strip()
                        ),
                        format_optional(failed_case.actual_result),
                        format_optional(failed_case.error),
                        " · ".join(
                            part
                            for part in (
                                None
                                if failed_case.suspected_cause is None
                                else label_value(language, failed_case.suspected_cause),
                                failed_case.cause_reason,
                            )
                            if part
                        )
                        or format_optional(None),
                    ]
                    for failed_case in report.failed_cases
                ],
            )
            if report.failed_cases
            else None,
            empty_text=None if report.failed_cases else translate(language, ReportText.NOTHING_TO_SHOW),
        )
    )
    if report.criterion_impacts:
        sections.append(
            ReportSection(
                heading=translate(language, ReportText.CRITERION_IMPACT),
                table=ReportTable(
                    headers=[
                        translate(language, key)
                        for key in (
                            ReportText.STORY,
                            ReportText.CRITERION,
                            ReportText.TEXT,
                            ReportText.STATUS,
                            ReportText.CASES_RUN,
                            ReportText.FAILING_CASES,
                        )
                    ],
                    rows=[
                        [
                            format_optional(impact.story_jira_key),
                            impact.code,
                            impact.text,
                            label_value(language, impact.status),
                            ", ".join(impact.run_case_codes) or format_optional(None),
                            ", ".join(impact.failed_case_codes) or format_optional(None),
                        ]
                        for impact in report.criterion_impacts
                    ],
                ),
            )
        )
    if report.skipped_cases:
        sections.append(
            ReportSection(
                heading=translate(language, ReportText.SKIPPED_CASES),
                table=ReportTable(
                    headers=[
                        translate(language, key)
                        for key in (ReportText.CASE, ReportText.TITLE, ReportText.STORY, ReportText.REASON)
                    ],
                    rows=[
                        [skipped.code, skipped.title, skipped.story_jira_key, label_value(language, skipped.reason)]
                        for skipped in report.skipped_cases
                    ],
                ),
            )
        )
    if report.missing_screenshots:
        sections.append(
            ReportSection(
                heading=translate(language, ReportText.MISSING_SCREENSHOTS),
                table=ReportTable(
                    headers=[
                        translate(language, key) for key in (ReportText.CASE, ReportText.STEP, ReportText.ITERATION)
                    ],
                    rows=[
                        [
                            missing.code,
                            str(missing.step_order),
                            format_optional(None if missing.iteration is None else str(missing.iteration + 1)),
                        ]
                        for missing in report.missing_screenshots
                    ],
                ),
            )
        )
    return sections


def describe_iterations(case_detail: RunCaseDetail, language: UserLanguage) -> str:
    if not case_detail.iterations:
        return format_optional(None)
    return ", ".join(
        f"#{iteration.iteration + 1} "
        + (
            translate(language, ReportText.NOT_REPORTED)
            if iteration.result is None
            else label_value(language, iteration.result.status)
        )
        for iteration in case_detail.iterations
    )


def build_case_section(cases: list[RunCaseDetail], language: UserLanguage) -> ReportSection:
    return ReportSection(
        heading=translate(language, ReportText.CASES),
        table=ReportTable(
            headers=[
                translate(language, key)
                for key in (
                    ReportText.CASE,
                    ReportText.TITLE,
                    ReportText.STORY,
                    ReportText.VERSION,
                    ReportText.STATUS,
                    ReportText.ITERATIONS,
                )
            ],
            rows=[
                [
                    case_detail.view.code,
                    case_detail.view.version.title,
                    format_optional(case_detail.view.story_jira_key),
                    f"v{case_detail.view.version.number}",
                    translate(language, ReportText.NOT_REPORTED)
                    if case_detail.result is None
                    else label_value(language, case_detail.result.status),
                    describe_iterations(case_detail, language),
                ]
                for case_detail in cases
            ],
        )
        if cases
        else None,
        empty_text=None if cases else translate(language, ReportText.NOTHING_TO_SHOW),
    )
