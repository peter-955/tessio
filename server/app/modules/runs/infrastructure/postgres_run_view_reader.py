from collections import defaultdict
from collections.abc import Collection
from uuid import UUID

from sqlalchemy import Row, Select, func, select

from app.modules.files import StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_file.entity import RunCaseFile
from app.modules.runs.domains.run_criterion.entity import RunCriterion
from app.modules.runs.domains.run_filter.entity import RunFilter
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.runs.infrastructure.case_result_table import CaseResultTable
from app.modules.runs.infrastructure.run_case_table import RunCaseTable
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.infrastructure.step_result_table import StepResultTable
from app.modules.runs.infrastructure.suite_name_table import SUITE_NAME_TABLE
from app.modules.runs.infrastructure.worst_iteration_condition import is_worst_iteration
from app.modules.runs.ports.run_view_reader import RunViewReader
from app.modules.runs.typing.enums import ResultStatus
from app.modules.runs.utils.run_counts import build_run_counts
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_cases.infrastructure import TestFileTable, TestFileVersionTable
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
        if run_filter.test_suite_id is not None:
            statement = statement.where(RunTable.test_suite_id == run_filter.test_suite_id)
        if run_filter.status is not None:
            statement = statement.where(RunTable.status == run_filter.status)
        result = await self._database.get_current_session().execute(
            statement.order_by(RunTable.started_at.desc(), RunTable.id.desc()).limit(run_filter.limit)
        )
        labelled_runs = [(Run.model_validate(row[0]), self._build_labels(row)) for row in result]
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
        return self._build_labels(result.one())

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

    async def map_active_criteria(self, criterion_ids: Collection[UUID]) -> dict[UUID, RunCriterion]:
        if not criterion_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(AcceptanceCriterionTable.id, AcceptanceCriterionTable.code, AcceptanceCriterionTable.text)
            .where(AcceptanceCriterionTable.id.in_(criterion_ids), AcceptanceCriterionTable.removed_at.is_(None))
            .order_by(AcceptanceCriterionTable.position)
        )
        return {criterion_id: RunCriterion(code=code, text=text) for criterion_id, code, text in result}

    async def map_case_files(self, file_version_ids: Collection[UUID]) -> dict[UUID, RunCaseFile]:
        if not file_version_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(TestFileVersionTable.id, TestFileTable.key, StoredFileTable.file_name)
            .join(TestFileTable, TestFileTable.id == TestFileVersionTable.test_file_id)
            .join(StoredFileTable, StoredFileTable.id == TestFileVersionTable.stored_file_id)
            .where(TestFileVersionTable.id.in_(file_version_ids))
        )
        return {
            file_version_id: RunCaseFile(key=key, file_name=file_name) for file_version_id, key, file_name in result
        }

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
            select(CaseResultTable.run_id, CaseResultTable.status).where(
                CaseResultTable.run_id.in_(run_ids), is_worst_iteration()
            )
        )
        statuses_by_run_id: defaultdict[UUID, list[ResultStatus]] = defaultdict(list)
        for run_id, status in result:
            statuses_by_run_id[run_id].append(status)
        return statuses_by_run_id

    @staticmethod
    def _build_labels(row: Row[RunTable, str | None, str | None, str, str, str, str | None]) -> RunLabels:
        _, story_jira_key, story_title, environment_name, environment_base_url, started_by_name, suite_name = row
        return RunLabels(
            story_jira_key=story_jira_key,
            story_title=story_title,
            environment_name=environment_name,
            environment_base_url=environment_base_url,
            started_by_name=started_by_name,
            test_suite_name=suite_name,
        )

    @staticmethod
    def _select_labelled_runs() -> Select[RunTable, str | None, str | None, str, str, str, str | None]:
        return (
            select(
                RunTable,
                StoryTable.jira_key,
                StoryTable.title,
                EnvironmentTable.name,
                EnvironmentTable.base_url,
                UserTable.name,
                SUITE_NAME_TABLE.c.name,
            )
            .outerjoin(StoryTable, StoryTable.id == RunTable.story_id)
            .outerjoin(SUITE_NAME_TABLE, SUITE_NAME_TABLE.c.id == RunTable.test_suite_id)
            .join(EnvironmentTable, EnvironmentTable.id == RunTable.environment_id)
            .join(UserTable, UserTable.id == RunTable.started_by)
        )
