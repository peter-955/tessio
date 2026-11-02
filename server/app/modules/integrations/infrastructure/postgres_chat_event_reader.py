from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.modules.failures.infrastructure import FailureTable
from app.modules.gaps.infrastructure import GapTable
from app.modules.integrations.domains.chat_failure_details.entity import ChatFailureDetails
from app.modules.integrations.domains.chat_gap_details.entity import ChatGapDetails
from app.modules.integrations.domains.chat_plan_details.entity import ChatPlanDetails
from app.modules.integrations.domains.chat_project.entity import ChatProject
from app.modules.integrations.domains.chat_run_details.entity import ChatRunDetails
from app.modules.integrations.domains.chat_story_details.entity import ChatStoryDetails
from app.modules.integrations.ports.chat_event_reader import ChatEventReader
from app.modules.integrations.typing.constants import CHAT_CASE_CODE_PREFIX
from app.modules.plans.infrastructure import TestPlanTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.infrastructure import RunTable
from app.modules.stories.infrastructure import StoryTable
from app.modules.suites.infrastructure import TestSuiteTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database

COUNT_KEYS = ("passed", "failed", "blocked", "skipped")


class PostgresChatEventReader(ChatEventReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_project(self, project_id: UUID) -> ChatProject | None:
        row = (
            await self._database.get_current_session().execute(
                select(ProjectTable.id, ProjectTable.key, ProjectTable.name).where(ProjectTable.id == project_id)
            )
        ).first()
        return None if row is None else ChatProject(id=row.id, key=row.key, name=row.name)

    async def find_run(self, project_id: UUID, run_id: UUID) -> ChatRunDetails | None:
        row = (
            await self._database.get_current_session().execute(
                select(
                    RunTable.id,
                    RunTable.status,
                    RunTable.executor,
                    RunTable.report,
                    EnvironmentTable.name.label("environment_name"),
                    UserTable.name.label("started_by_name"),
                    StoryTable.jira_key,
                    StoryTable.title,
                    TestSuiteTable.name.label("suite_name"),
                )
                .join(EnvironmentTable, EnvironmentTable.id == RunTable.environment_id)
                .join(UserTable, UserTable.id == RunTable.started_by)
                .outerjoin(StoryTable, StoryTable.id == RunTable.story_id)
                .outerjoin(TestSuiteTable, TestSuiteTable.id == RunTable.test_suite_id)
                .where(RunTable.id == run_id, RunTable.project_id == project_id)
            )
        ).first()
        if row is None:
            return None
        counts = read_report_counts(row.report)
        return ChatRunDetails(
            id=row.id,
            status=str(row.status),
            executor=str(row.executor),
            environment_name=row.environment_name,
            started_by_name=row.started_by_name,
            story_jira_key=row.jira_key,
            story_title=row.title,
            suite_name=row.suite_name,
            passed_count=counts.get("passed"),
            failed_count=counts.get("failed"),
            blocked_count=counts.get("blocked"),
            skipped_count=counts.get("skipped"),
        )

    async def find_failure(self, project_id: UUID, failure_id: UUID) -> ChatFailureDetails | None:
        row = (
            await self._database.get_current_session().execute(
                select(
                    FailureTable.id,
                    FailureTable.status,
                    TestCaseTable.number,
                    TestCaseTable.title,
                    StoryTable.jira_key,
                    UserTable.name.label("assignee_name"),
                )
                .join(TestCaseTable, TestCaseTable.id == FailureTable.test_case_id)
                .join(StoryTable, StoryTable.id == FailureTable.story_id)
                .outerjoin(UserTable, UserTable.id == FailureTable.assignee_id)
                .where(FailureTable.id == failure_id, FailureTable.project_id == project_id)
            )
        ).first()
        if row is None:
            return None
        return ChatFailureDetails(
            id=row.id,
            status=str(row.status),
            test_case_code=f"{CHAT_CASE_CODE_PREFIX}{row.number}",
            test_case_title=row.title,
            story_jira_key=row.jira_key,
            assignee_name=row.assignee_name,
        )

    async def find_gap(self, project_id: UUID, gap_id: UUID) -> ChatGapDetails | None:
        raiser = aliased(UserTable)
        assignee = aliased(UserTable)
        row = (
            await self._database.get_current_session().execute(
                select(
                    GapTable.id,
                    GapTable.question,
                    GapTable.severity,
                    GapTable.assignee_role,
                    StoryTable.jira_key,
                    StoryTable.title,
                    raiser.name.label("raised_by_name"),
                    assignee.name.label("assignee_name"),
                )
                .join(StoryTable, StoryTable.id == GapTable.story_id)
                .join(raiser, raiser.id == GapTable.raised_by)
                .outerjoin(assignee, assignee.id == GapTable.assignee_id)
                .where(GapTable.id == gap_id, GapTable.project_id == project_id)
            )
        ).first()
        if row is None:
            return None
        return ChatGapDetails(
            id=row.id,
            story_jira_key=row.jira_key,
            story_title=row.title,
            question=row.question,
            severity=str(row.severity),
            assignee_name=row.assignee_name,
            assignee_role=None if row.assignee_role is None else str(row.assignee_role),
            raised_by_name=row.raised_by_name,
        )

    async def find_story(self, project_id: UUID, story_id: UUID) -> ChatStoryDetails | None:
        row = (
            await self._database.get_current_session().execute(
                select(
                    StoryTable.id,
                    StoryTable.jira_key,
                    StoryTable.title,
                    StoryTable.test_status,
                    UserTable.name.label("signed_off_by_name"),
                )
                .outerjoin(UserTable, UserTable.id == StoryTable.test_status_changed_by)
                .where(StoryTable.id == story_id, StoryTable.project_id == project_id)
            )
        ).first()
        if row is None:
            return None
        return ChatStoryDetails(
            id=row.id,
            jira_key=row.jira_key,
            title=row.title,
            test_status=str(row.test_status),
            signed_off_by_name=row.signed_off_by_name,
        )

    async def find_plan(self, project_id: UUID, plan_id: UUID) -> ChatPlanDetails | None:
        row = (
            await self._database.get_current_session().execute(
                select(
                    TestPlanTable.id,
                    TestPlanTable.name,
                    TestPlanTable.target_date,
                    UserTable.name.label("signed_off_by_name"),
                )
                .outerjoin(UserTable, UserTable.id == TestPlanTable.signed_off_by)
                .where(TestPlanTable.id == plan_id, TestPlanTable.project_id == project_id)
            )
        ).first()
        if row is None:
            return None
        return ChatPlanDetails(
            id=row.id, name=row.name, signed_off_by_name=row.signed_off_by_name, target_date=row.target_date
        )


def read_report_counts(report: JsonValue) -> dict[str, int]:
    if not isinstance(report, dict):
        return {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        return {}
    return {key: value for key in COUNT_KEYS if isinstance(value := counts.get(key), int)}
