from collections.abc import Collection
from uuid import UUID, uuid4

from sqlalchemy import delete, select

from app.container import Container
from app.modules.notifications import (
    FailureAssignedPayload,
    GapAssignedPayload,
    Notification,
    NotificationPayload,
    RunFinishedPayload,
    RunOutcome,
)
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.projects.infrastructure import ProjectMemberTable
from app.shared.permissions import ProjectRole
from tests.api.test_data.project_steps import SeededProject


def build_gap_payload(question: str = "Which currencies does checkout accept?") -> GapAssignedPayload:
    return GapAssignedPayload(gap_id=uuid4(), story_id=uuid4(), story_jira_key="SHOP-12", question=question)


def build_failure_payload() -> FailureAssignedPayload:
    return FailureAssignedPayload(
        failure_id=uuid4(),
        test_case_id=uuid4(),
        test_case_code="TC-12",
        test_case_title="Pay with a saved card",
        story_jira_key="SHOP-12",
    )


def build_run_payload(outcome: RunOutcome = RunOutcome.PASSED) -> RunFinishedPayload:
    return RunFinishedPayload(
        run_id=uuid4(),
        story_id=uuid4(),
        story_jira_key="SHOP-12",
        outcome=outcome,
        passed_count=8,
        failed_count=1,
        blocked_count=0,
    )


async def send_notification(
    container: Container,
    project: SeededProject,
    payload: NotificationPayload,
    actor_id: UUID | None,
    recipient_ids: Collection[UUID] = (),
    recipient_roles: Collection[ProjectRole] = (),
) -> list[Notification]:
    return await container.send_notification.execute(project.id, payload, actor_id, recipient_ids, recipient_roles)


async def send_gap_assigned(
    container: Container, project: SeededProject, recipient_id: UUID, actor_id: UUID | None
) -> Notification:
    notifications = await send_notification(container, project, build_gap_payload(), actor_id, {recipient_id})
    assert len(notifications) == 1
    return notifications[0]


async def list_stored_notifications(container: Container, user_id: UUID) -> list[NotificationTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.user_id == user_id).order_by(NotificationTable.id)
        )
        return list(rows)


async def remove_member(container: Container, project: SeededProject, user_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            delete(ProjectMemberTable).where(
                ProjectMemberTable.project_id == project.id, ProjectMemberTable.user_id == user_id
            )
        )
