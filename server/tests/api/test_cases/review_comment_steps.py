from dataclasses import dataclass
from datetime import UTC, datetime

from httpx import AsyncClient, Response
from pydantic import JsonValue
from sqlalchemy import update

from app.container import Container
from app.modules.projects.infrastructure import ProjectTable
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as, use_session
from tests.api.test_cases.case_steps import SeededStory, build_step, change_status, create_case_code, seed_story
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer

AUTHOR_NAME = "Ada Author"
REVIEWER_NAME = "Rex Reviewer"


@dataclass(frozen=True)
class ReviewProject:
    project: SeededProject
    story: SeededStory
    author: SignedUpAccount
    reviewer: SignedUpAccount
    case_code: str

    @property
    def key(self) -> str:
        return self.project.key

    @property
    def comments_path(self) -> str:
        return f"/api/projects/{self.key}/test-cases/{self.case_code}/review-comments"


async def sign_up_project_member(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole,
    name: str,
) -> SignedUpAccount:
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, name)
    await add_member(container, project, account.user_id, role)
    return account


async def set_up_review_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> ReviewProject:
    project = await seed_project(container)
    reviewer = await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.QC, REVIEWER_NAME)
    author = await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.QC, AUTHOR_NAME)
    story = await seed_story(container, project, f"{project.key}-1", ["Pay by card"])
    case_code = await create_case_code(
        client,
        project.key,
        story.jira_key,
        steps=[build_step("Open the checkout", "The card form shows"), build_step("Pay", "A receipt shows")],
    )
    in_review = await change_status(client, project.key, case_code, "in_review")
    assert in_review.status_code == 200, in_review.text
    return ReviewProject(project=project, story=story, author=author, reviewer=reviewer, case_code=case_code)


async def add_comment(client: AsyncClient, review_project: ReviewProject, **fields: JsonValue) -> Response:
    return await client.post(review_project.comments_path, json={"body": "Step 2 needs the amount.", **fields})


async def add_comment_id(client: AsyncClient, review_project: ReviewProject, **fields: JsonValue) -> str:
    response = await add_comment(client, review_project, **fields)
    assert response.status_code == 201, response.text
    comment_id: str = response.json()["id"]
    return comment_id


async def resolve_comment(client: AsyncClient, review_project: ReviewProject, comment_id: str) -> Response:
    return await client.put(f"{review_project.comments_path}/{comment_id}/resolve")


async def list_comments(client: AsyncClient, review_project: ReviewProject) -> list[dict[str, JsonValue]]:
    response = await client.get(review_project.comments_path)
    assert response.status_code == 200, response.text
    comments: list[dict[str, JsonValue]] = response.json()
    return comments


async def set_require_separate_reviewer(container: Container, project: SeededProject, is_required: bool) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(require_separate_reviewer=is_required)
        )


async def flag_needs_review(container: Container, review_project: ReviewProject) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable)
            .where(TestCaseTable.project_id == review_project.project.id)
            .values(needs_review_at=datetime.now(UTC), needs_review_criterion_ids=review_project.story.criterion_ids)
        )


def act_as(client: AsyncClient, account: SignedUpAccount) -> None:
    use_session(client, account.session_token)
