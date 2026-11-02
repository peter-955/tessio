from datetime import datetime
from uuid import UUID

from app.modules.insights import GetTraceabilityUseCase
from app.modules.notifications import ReportSource
from app.modules.plans import GetPlanUseCase
from app.modules.reports.domains.report_document.entity import ReportDocument
from app.modules.reports.domains.report_label.entity import ReportLabel
from app.modules.reports.errors import ReportSourceNotFoundError
from app.modules.reports.typing.constants import MAX_STORY_REPORT_RUNS
from app.modules.reports.utils.plan_report_document import build_plan_document
from app.modules.reports.utils.run_report_document import (
    build_run_document,
    describe_run_file_label,
    describe_run_label,
)
from app.modules.reports.utils.story_report_document import build_story_document
from app.modules.runs import GetRunUseCase, ListRunsUseCase
from app.modules.users import UserLanguage
from app.shared.permissions import Actor


def parse_source_uuid(source_id: str) -> UUID:
    try:
        return UUID(source_id)
    except ValueError as error:
        raise ReportSourceNotFoundError from error


class ReportDocumentLoader:
    def __init__(
        self,
        get_run: GetRunUseCase,
        get_plan: GetPlanUseCase,
        get_traceability: GetTraceabilityUseCase,
        list_runs: ListRunsUseCase,
    ) -> None:
        self._get_run = get_run
        self._get_plan = get_plan
        self._get_traceability = get_traceability
        self._list_runs = list_runs

    async def load(
        self,
        actor: Actor,
        project_key: str,
        source: ReportSource,
        source_id: str,
        language: UserLanguage,
        generated_at: datetime,
    ) -> tuple[ReportDocument, ReportLabel]:
        match source:
            case ReportSource.RUN:
                run_detail = await self._get_run.execute(actor, project_key, parse_source_uuid(source_id))
                run_label = describe_run_label(run_detail)
                return build_run_document(run_detail, language, generated_at), ReportLabel(
                    source_id=str(run_detail.run.id),
                    label=run_label,
                    file_stem=f"run-{describe_run_file_label(run_detail)}-{run_detail.run.started_at:%Y-%m-%d}",
                )
            case ReportSource.PLAN:
                plan_detail = await self._get_plan.execute(actor, project_key, parse_source_uuid(source_id))
                return build_plan_document(plan_detail, language, generated_at), ReportLabel(
                    source_id=str(plan_detail.plan.id),
                    label=plan_detail.plan.name,
                    file_stem=f"plan-{plan_detail.plan.name}",
                )
            case ReportSource.STORY:
                traceability = await self._get_traceability.execute(actor, project_key, source_id)
                story_runs = await self._list_runs.execute(
                    actor, project_key, traceability.story.jira_key, None, MAX_STORY_REPORT_RUNS
                )
                story = traceability.story
                return build_story_document(traceability, story_runs, language, generated_at), ReportLabel(
                    source_id=story.jira_key,
                    label=f"{story.jira_key} {story.title}",
                    file_stem=f"story-{story.jira_key}",
                )
