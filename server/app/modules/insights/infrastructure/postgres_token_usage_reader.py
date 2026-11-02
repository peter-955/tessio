from datetime import datetime
from uuid import UUID

from sqlalchemy import Text, func, select, type_coerce

from app.modules.insights.domains.token_run.entity import TokenRun
from app.modules.insights.ports.token_usage_reader import TokenUsageReader
from app.modules.run_logs.infrastructure import RunLogTable
from app.modules.runs.infrastructure import SUITE_NAME_TABLE, RunCaseTable, RunTable
from app.modules.stories.infrastructure import StoryTable
from app.shared.postgres import Database


class PostgresTokenUsageReader(TokenUsageReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_token_runs(
        self, project_id: UUID, start_at: datetime, end_at: datetime, limit: int
    ) -> list[TokenRun]:
        case_count = (
            select(func.count(RunCaseTable.id))
            .where(RunCaseTable.run_id == RunTable.id)
            .correlate(RunTable)
            .scalar_subquery()
        )
        result = await self._database.get_current_session().execute(
            select(
                RunTable.id,
                RunTable.started_at,
                type_coerce(RunTable.executor, Text),
                StoryTable.jira_key,
                SUITE_NAME_TABLE.c.name,
                case_count,
                RunLogTable.input_tokens,
                RunLogTable.cache_creation_input_tokens,
                RunLogTable.cache_read_input_tokens,
                RunLogTable.output_tokens,
                RunLogTable.is_cut,
            )
            .join(RunLogTable, RunLogTable.run_id == RunTable.id)
            .outerjoin(StoryTable, StoryTable.id == RunTable.story_id)
            .outerjoin(SUITE_NAME_TABLE, SUITE_NAME_TABLE.c.id == RunTable.test_suite_id)
            .where(
                RunTable.project_id == project_id,
                RunTable.started_at >= start_at,
                RunTable.started_at < end_at,
                RunLogTable.input_tokens
                + RunLogTable.cache_creation_input_tokens
                + RunLogTable.cache_read_input_tokens
                + RunLogTable.output_tokens
                > 0,
            )
            .order_by(RunTable.started_at.desc(), RunTable.id.desc())
            .limit(limit)
        )
        return [
            TokenRun(
                run_id=run_id,
                started_at=started_at,
                executor=str(executor),
                story_jira_key=jira_key,
                test_suite_name=suite_name,
                case_count=cases or 0,
                input_tokens=input_tokens,
                cache_creation_input_tokens=cache_creation_tokens,
                cache_read_input_tokens=cache_read_tokens,
                output_tokens=output_tokens,
                is_cut=is_cut,
            )
            for (
                run_id,
                started_at,
                executor,
                jira_key,
                suite_name,
                cases,
                input_tokens,
                cache_creation_tokens,
                cache_read_tokens,
                output_tokens,
                is_cut,
            ) in result
        ]
