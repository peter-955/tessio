from datetime import datetime

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_fact.entity import ReportFact
from app.modules.reports.domains.report_section.entity import ReportSection
from app.modules.reports.typing.enums import ReportText
from app.modules.reports.utils.report_text import (
    format_day,
    format_moment,
    format_optional,
    label_value,
    translate,
)
from app.modules.reports.utils.table_section import build_table_section
from app.modules.users import UserLanguage


def build_plan_document(detail: PlanDetail, language: UserLanguage, generated_at: datetime) -> ReportDocument:
    plan = detail.plan
    progress = detail.progress
    counts = progress.counts
    facts = [
        ReportFact(label=translate(language, ReportText.STATUS), value=label_value(language, plan.status)),
        ReportFact(label=translate(language, ReportText.TARGET_DATE), value=format_day(plan.target_date)),
        ReportFact(label=translate(language, ReportText.ENVIRONMENT), value=format_optional(detail.environment_name)),
        ReportFact(label=translate(language, ReportText.CREATED), value=format_moment(plan.created_at)),
    ]
    if plan.signed_off_at is not None:
        signer = None if plan.signed_off_by is None else detail.user_names.get(plan.signed_off_by)
        facts.append(
            ReportFact(
                label=translate(language, ReportText.SIGNED_OFF),
                value=" · ".join(part for part in (format_moment(plan.signed_off_at), signer) if part),
            )
        )
    if plan.closed_at is not None:
        facts.append(ReportFact(label=translate(language, ReportText.CLOSED), value=format_moment(plan.closed_at)))
    facts.append(ReportFact(label=translate(language, ReportText.GENERATED_AT), value=format_moment(generated_at)))
    sections: list[ReportSection] = []
    if plan.description:
        sections.append(
            ReportSection(heading=translate(language, ReportText.DESCRIPTION), paragraphs=[plan.description])
        )
    sections.append(
        build_table_section(
            translate(language, ReportText.PROGRESS),
            [
                translate(language, key)
                for key in (
                    ReportText.TOTAL,
                    ReportText.PASSED,
                    ReportText.FAILED,
                    ReportText.BLOCKED,
                    ReportText.SKIPPED,
                    ReportText.NOT_RUN,
                )
            ],
            [
                [
                    str(value)
                    for value in (
                        counts.total,
                        counts.passed,
                        counts.failed,
                        counts.blocked,
                        counts.skipped,
                        counts.not_run,
                    )
                ]
            ],
            language,
        )
    )
    sections.append(
        build_table_section(
            translate(language, ReportText.SCOPE),
            [
                translate(language, key)
                for key in (ReportText.KIND, ReportText.NAME, ReportText.CASE_COUNT, ReportText.ARCHIVED)
            ],
            [
                [
                    label_value(language, item.kind),
                    item.name if item.story_jira_key is None else f"{item.story_jira_key} {item.name}",
                    str(item.case_count),
                    format_moment(item.archived_at) if item.archived_at is not None else format_optional(None),
                ]
                for item in detail.items
            ],
            language,
        )
    )
    sections.append(
        build_table_section(
            translate(language, ReportText.CASES),
            [
                translate(language, key)
                for key in (
                    ReportText.CASE,
                    ReportText.TITLE,
                    ReportText.STORY,
                    ReportText.STATUS,
                    ReportText.LATEST_RESULT,
                    ReportText.ACTIVE_FAILURE,
                )
            ],
            [
                [
                    case_progress.case.code,
                    case_progress.case.title,
                    case_progress.case.story_jira_key,
                    label_value(language, case_progress.case.status),
                    translate(language, ReportText.NOT_RUN)
                    if case_progress.latest_result is None
                    else label_value(language, case_progress.latest_result.status),
                    format_optional(
                        None
                        if case_progress.active_failure is None
                        else label_value(language, case_progress.active_failure.status)
                    ),
                ]
                for case_progress in progress.cases
            ],
            language,
        )
    )
    sections.append(
        build_table_section(
            translate(language, ReportText.ACTIVE_FAILURES),
            [
                translate(language, key)
                for key in (
                    ReportText.CASE,
                    ReportText.TITLE,
                    ReportText.STORY,
                    ReportText.STATUS,
                    ReportText.ASSIGNEE,
                    ReportText.OPENED,
                )
            ],
            [
                [
                    failure.code,
                    failure.title,
                    failure.story_jira_key,
                    label_value(language, failure.status),
                    format_optional(failure.assignee_name),
                    format_moment(failure.created_at),
                ]
                for failure in progress.failures
            ],
            language,
        )
    )
    sections.append(
        build_table_section(
            translate(language, ReportText.OPEN_GAPS),
            [
                translate(language, key)
                for key in (
                    ReportText.STORY,
                    ReportText.QUESTION,
                    ReportText.SEVERITY,
                    ReportText.ASSIGNEE,
                    ReportText.OPENED,
                )
            ],
            [
                [
                    gap.story_jira_key,
                    gap.question,
                    label_value(language, gap.severity),
                    format_optional(gap.assignee_name or (None if gap.assignee_role is None else gap.assignee_role)),
                    format_moment(gap.created_at),
                ]
                for gap in progress.gaps
            ],
            language,
        )
    )
    return ReportDocument(
        title=f"{translate(language, ReportText.PLAN_TITLE)} · {plan.name}",
        subtitle=str(plan.id),
        facts=facts,
        sections=sections,
    )
