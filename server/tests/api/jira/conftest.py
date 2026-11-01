import pytest
from sqlalchemy import delete

from app.container import Container
from app.modules.jira.infrastructure import JiraConnectionTable
from tests.fakes.fake_jira_client import FakeJiraClient


@pytest.fixture
def fake_jira_client(container: Container) -> FakeJiraClient:
    jira_client = container.jira_client
    assert isinstance(jira_client, FakeJiraClient)
    return jira_client


@pytest.fixture(autouse=True)
async def clear_jira_connection(container: Container) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(delete(JiraConnectionTable))
