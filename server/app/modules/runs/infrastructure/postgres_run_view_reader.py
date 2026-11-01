from collections import defaultdict
from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Select, func, select

from app.modules.files import StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_filter.entity import RunFilter
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.runs.infrastructure.case_result_table import CaseResultTable
from app.modules.runs.infrastructure.run_case_table import RunCaseTable
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.infrastructure.step_result_table import StepResultTable
from app.modules.runs.ports.run_view_reader import RunViewReader
from app.modules.runs.typing.enums import ResultStatus
from app.modules.runs.utils.run_counts import build_run_counts
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresRunViewReader(RunViewReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_summaries(self, project_id: UUID, run_filter: RunFilter) -> list[RunSummary]:
        statement = self._select_labelled_runs().where(RunTable.project_id == project_id)
        if run_filter.story_id is not None:
            statement = statement.where(RunTable.story_id == run_filter.story_id)
        if run_filter.status is not None:
            statement = statement.where(RunTable.status == run_filter.status)
        result = await self._database.get_current_session().execute(
            statement.order_by(RunTable.started_at.desc(), RunTable.id.desc()).limit(run_filter.limit)
        )
        labelled_runs = [
            (
                Run.model_validate(run_row),
                RunLabels(
                    story_jira_key=story_jira_key,
                    story_title=story_title,
                    environment_name=environment_name,
                    started_by_name=started_by_name,
                ),
            )
            for run_row, story_jira_key, story_title, environment_name, started_by_name in result
        ]
        run_ids = [run.id for run, _ in labelled_runs]
        case_totals = await self._count_run_cases(run_ids)
        result_statuses = await self._list_result_statuses(run_ids)
        return [
            RunSummary(
                run=run,
                labels=labels,
                counts=build_run_counts(case_totals.get(run.id, 0), result_statuses.get(run.id, [])),
            )
            for run, labels in labelled_runs
        ]

    async def find_labels(self, run: Run) -> RunLabels:
        result = await self._database.get_current_session().execute(
            self._select_labelled_runs().where(RunTable.id == run.id)
        )
        _, story_jira_key, story_title, environment_name, started_by_name = result.one()
        return RunLabels(
            story_jira_key=story_jira_key,
            story_title=story_title,
            environment_name=environment_name,
            started_by_name=started_by_name,
        )

    async def list_screenshot_statuses(self, run_id: UUID) -> dict[UUID, StoredFileStatus]:
        result = await self._database.get_current_session().execute(
            select(StoredFileTable.id, StoredFileTable.status)
            .join(StepResultTable, StepResultTable.screenshot_file_id == StoredFileTable.id)
            .join(CaseResultTable, CaseResultTable.id == StepResultTable.case_result_id)
            .where(CaseResultTable.run_id == run_id)
        )
        return {row.id: row.status for row in result}

    async def list_child_run_ids(self, run_id: UUID) -> list[UUID]:
        child_run_ids = await self._database.get_current_session().scalars(
            select(RunTable.id).where(RunTable.parent_run_id == run_id).order_by(RunTable.started_at, RunTable.id)
        )
        return list(child_run_ids)

    async def _count_run_cases(self, run_ids: Collection[UUID]) -> dict[UUID, int]:
        if not run_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(RunCaseTable.run_id, func.count(RunCaseTable.id).label("case_count"))
            .where(RunCaseTable.run_id.in_(run_ids))
            .group_by(RunCaseTable.run_id)
        )
        return {row.run_id: row.case_count for row in result}

    async def _list_result_statuses(self, run_ids: Collection[UUID]) -> dict[UUID, list[ResultStatus]]:
        if not run_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(CaseResultTable.run_id, CaseResultTable.status).where(CaseResultTable.run_id.in_(run_ids))
        )
        statuses_by_run_id: defaultdict[UUID, list[ResultStatus]] = defaultdict(list)
        for run_id, status in result:
            statuses_by_run_id[run_id].append(status)
        return statuses_by_run_id

    @staticmethod
    def _select_labelled_runs() -> Select[RunTable, str, str, str, str]:
        return (
            select(RunTable, StoryTable.jira_key, StoryTable.title, EnvironmentTable.name, UserTable.name)
            .join(StoryTable, StoryTable.id == RunTable.story_id)
            .join(EnvironmentTable, EnvironmentTable.id == RunTable.environment_id)
            .join(UserTable, UserTable.id == RunTable.started_by)
        )
