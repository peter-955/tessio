import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import DatabaseSettings
from app.modules.api_tokens.infrastructure import ApiTokenTable
from app.modules.audit.infrastructure import AuditEventTable
from app.modules.auth.infrastructure import OneTimeTokenTable, RecoveryCodeTable, UserSessionTable
from app.modules.failures.infrastructure import FailureEventTable, FailureTable
from app.modules.files.infrastructure import StoredFileTable
from app.modules.gaps.infrastructure import GapTable
from app.modules.jira.infrastructure import JiraConnectionTable
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.projects.infrastructure import ProjectMemberTable, ProjectTable
from app.modules.runs.infrastructure import CaseResultTable, RunCaseTable, RunFileTable, RunTable, StepResultTable
from app.modules.stories.infrastructure import AcceptanceCriterionTable, ProjectSyncStateTable, SprintTable, StoryTable
from app.modules.test_cases.infrastructure import (
    TestCaseCounterTable,
    TestCaseCriterionTable,
    TestCaseTable,
    TestCaseVersionTable,
    TestFileTable,
    TestFileVersionTable,
)
from app.modules.test_data.infrastructure import DataItemTable, EnvironmentTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import TableBase

TABLES = [
    UserTable,
    UserSessionTable,
    RecoveryCodeTable,
    OneTimeTokenTable,
    ProjectTable,
    ProjectMemberTable,
    ApiTokenTable,
    StoredFileTable,
    AuditEventTable,
    JiraConnectionTable,
    EnvironmentTable,
    DataItemTable,
    SprintTable,
    StoryTable,
    AcceptanceCriterionTable,
    ProjectSyncStateTable,
    TestCaseCounterTable,
    TestCaseTable,
    TestCaseVersionTable,
    TestCaseCriterionTable,
    TestFileTable,
    TestFileVersionTable,
    NotificationTable,
    GapTable,
    RunTable,
    RunCaseTable,
    CaseResultTable,
    StepResultTable,
    RunFileTable,
    FailureTable,
    FailureEventTable,
]

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name, disable_existing_loggers=False)


def read_database_url() -> str:
    configured_url = context.config.get_main_option("sqlalchemy.url")
    return configured_url or DatabaseSettings().database_url


def run_migrations_offline() -> None:
    context.configure(url=read_database_url(), target_metadata=TableBase.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def apply_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=TableBase.metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(read_database_url())
    async with engine.connect() as connection:
        await connection.run_sync(apply_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
