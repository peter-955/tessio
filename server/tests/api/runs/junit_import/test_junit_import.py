from httpx import AsyncClient
from sqlalchemy import func, select, update

from app.container import Container
from app.modules.projects import JiraPostResults
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.infrastructure import RunTable
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName
from tests.api.projects.user_steps import use_session
from tests.api.runs.junit_import.junit_import_steps import import_junit, read_fixture, seed_import_world
from tests.api.runs.run_steps import change_case_status, seed_secret
from tests.api.security.security_steps import read_code
from tests.api.suites.suite_steps import create_suite_id, set_suite_cases
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def count_runs(container: Container, project_id: object) -> int:
    async with container.database.begin():
        count = await container.database.get_current_session().scalar(
            select(func.count()).select_from(RunTable).where(RunTable.project_id == project_id)
        )
    return int(count or 0)


async def test_a_playwright_report_becomes_a_finished_ci_run_with_results_and_failures(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_import_world(client, container, recording_mailer)
    recording_live_event_publisher.events.clear()

    response = await import_junit(client, world.project.key, read_fixture("playwright.xml"))

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "failed"
    assert body["counts"] == {"total": 4, "passed": 2, "failed": 1, "blocked": 0, "skipped": 1, "notReported": 0}
    assert body["mappedTestCount"] == 4
    assert body["unmappedTestCount"] == 1
    assert body["unmappedTests"] == [
        {
            "name": "checkout \u203a shows the footer",
            "classname": "checkout.spec.ts",
            "status": "passed",
            "reason": "no_case_code",
        }
    ]
    run = (await client.get(f"/api/projects/{world.project.key}/runs/{body['runId']}")).json()
    assert run["executor"] == "ci"
    assert run["status"] == "failed"
    assert run["storyId"] is None
    assert run["testSuiteId"] is None
    assert run["finishedAt"] is not None
    assert run["report"]["unmappedTestCount"] == 1
    assert run["report"]["unmappedTests"][0]["reason"] == "no_case_code"
    assert [case["code"] for case in run["cases"]] == ["TC-1", "TC-2", "TC-3", "TC-4"]
    assert [case["result"]["status"] for case in run["cases"]] == ["passed", "failed", "passed", "skipped"]
    assert run["cases"][0]["result"]["durationMs"] == 3210
    failed_step = run["cases"][1]["steps"][0]
    assert failed_step["status"] == "failed"
    assert failed_step["error"] == "checkout.spec.ts:20:5 TC-2 refuses an expired card"
    assert run["report"]["failedCases"][0]["code"] == "TC-2"
    failures = (await client.get(f"/api/projects/{world.project.key}/failures")).json()
    assert [(failure["testCaseId"], failure["status"]) for failure in failures] == [
        (str(world.story.case_ids[1]), "open")
    ]
    event_types = [event.type for event in recording_live_event_publisher.events]
    assert event_types[0] is LiveEventType.RUN_STARTED
    assert event_types[-1] is LiveEventType.RUN_FINISHED
    assert event_types.count(LiveEventType.RUN_CASE_RECORDED) == 4
    opened = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.FAILURE_OPENED]
    assert len(opened) == 1
    assert opened[0].ids["runId"] == body["runId"]
    assert opened[0].ids["testCaseId"] == str(world.story.case_ids[1])
    assert opened[0].ids["failureId"] == failures[0]["id"]


async def test_jest_and_pytest_reports_map_their_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer)

    jest = await import_junit(client, world.project.key, read_fixture("jest.xml"))
    pytest_report = await import_junit(client, world.project.key, read_fixture("pytest.xml"))

    assert jest.status_code == 201, jest.text
    assert jest.json()["counts"]["passed"] == 1
    assert jest.json()["counts"]["failed"] == 1
    assert [test["name"] for test in jest.json()["unmappedTests"]] == ["Login remembers the email"]
    assert pytest_report.status_code == 201, pytest_report.text
    assert pytest_report.json()["counts"] == {
        "total": 4,
        "passed": 1,
        "failed": 2,
        "blocked": 0,
        "skipped": 1,
        "notReported": 0,
    }
    assert [test["name"] for test in pytest_report.json()["unmappedTests"]] == ["test_unrelated_helper"]
    runs = (await client.get(f"/api/projects/{world.project.key}/runs")).json()
    assert [run["executor"] for run in runs] == ["ci", "ci"]


async def test_a_ci_job_imports_with_an_api_scope_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer)
    created = await client.post(
        "/api/me/api-tokens", json={"name": "GitHub Actions", "projectKey": world.project.key, "scope": "api"}
    )
    token = created.json()["token"]
    client.cookies.clear()

    response = await import_junit(
        client, world.project.key, read_fixture("pytest.xml"), headers={"authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201, response.text
    run = await client.get(
        f"/api/projects/{world.project.key}/runs/{response.json()['runId']}",
        headers={"authorization": f"Bearer {token}"},
    )
    assert run.status_code == 200
    assert run.json()["executor"] == "ci"


async def test_an_import_into_a_suite_belongs_to_the_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.project.key, "Nightly")
    assert (await set_suite_cases(client, world.project.key, suite_id, world.story.case_ids)).status_code == 200

    response = await import_junit(client, world.project.key, read_fixture("playwright.xml"), suite="nightly")

    assert response.status_code == 201, response.text
    run = (await client.get(f"/api/projects/{world.project.key}/runs/{response.json()['runId']}")).json()
    assert run["testSuiteId"] == suite_id
    assert run["testSuiteName"] == "Nightly"
    suite_runs = (await client.get(f"/api/projects/{world.project.key}/runs", params={"suiteId": suite_id})).json()
    assert [suite_run["id"] for suite_run in suite_runs] == [response.json()["runId"]]


async def test_an_untargeted_import_is_the_last_run_of_the_stories_it_covers(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer)

    response = await import_junit(client, world.project.key, read_fixture("playwright.xml"))

    assert response.status_code == 201, response.text
    progress = (await client.get(f"/api/projects/{world.project.key}/story-progress")).json()
    story_progress = next(item for item in progress if item["storyId"] == str(world.story.story_id))
    assert story_progress["lastRun"]["id"] == response.json()["runId"]
    assert story_progress["lastRun"]["status"] == "failed"


async def test_an_import_asks_for_the_jira_result_comment_of_each_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    world = await seed_import_world(client, container, recording_mailer)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable)
            .where(ProjectTable.id == world.project.id)
            .values(jira_post_results=JiraPostResults.EVERY_RUN)
        )

    response = await import_junit(client, world.project.key, read_fixture("playwright.xml"))

    assert response.status_code == 201, response.text
    jobs = [job for job in recording_job_queue.jobs if job.job_name is JobName.JIRA_POST_COMMENT]
    assert [(job.data["storyId"], job.data["runId"]) for job in jobs] == [
        (str(world.story.story_id), response.json()["runId"])
    ]


async def test_a_duration_longer_than_a_day_is_dropped(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer, case_count=2)
    content = b"<testsuite><testcase name='TC-1 big' time='99999999'/><testcase name='TC-2 ok' time='2'/></testsuite>"

    response = await import_junit(client, world.project.key, content)

    assert response.status_code == 201, response.text
    run = (await client.get(f"/api/projects/{world.project.key}/runs/{response.json()['runId']}")).json()
    assert [case["result"]["durationMs"] for case in run["cases"]] == [None, 2000]


async def test_a_deprecated_or_unknown_case_is_listed_as_unknown(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer, case_count=2)
    await change_case_status(container, world.story.case_ids[1], "deprecated")
    content = (
        b"<testsuite><testcase name='TC-1 works'/><testcase name='TC-2 old'/>"
        b"<testcase name='TC-404 missing'/></testsuite>"
    )

    response = await import_junit(client, world.project.key, content)

    assert response.status_code == 201, response.text
    assert [(test["name"], test["reason"]) for test in response.json()["unmappedTests"]] == [
        ("TC-2 old", "unknown_case"),
        ("TC-404 missing", "unknown_case"),
    ]


async def test_secrets_in_failure_messages_are_masked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer, case_count=1)
    await seed_secret(container, world.project, "admin_password", "Sup3r-Secret!")
    content = (
        b"<testsuite><testcase name='TC-1 signs in'>"
        b"<failure message='login with Sup3r-Secret! failed'/></testcase></testsuite>"
    )

    response = await import_junit(client, world.project.key, content)

    run = (await client.get(f"/api/projects/{world.project.key}/runs/{response.json()['runId']}")).json()
    error = run["cases"][0]["steps"][0]["error"]
    assert "Sup3r-Secret!" not in error
    assert error.startswith("login with ")


async def test_a_file_without_mapped_tests_creates_no_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer, case_count=1)

    response = await import_junit(client, world.project.key, b"<testsuite><testcase name='no code'/></testsuite>")

    assert response.status_code == 422
    assert read_code(response) == "JUNIT_NO_MAPPED_TESTS"
    assert await count_runs(container, world.project.id) == 0


async def test_invalid_files_and_references_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer)

    bomb = await import_junit(client, world.project.key, read_fixture("billion_laughs.xml"))
    external = await import_junit(client, world.project.key, read_fixture("external_entity.xml"))
    broken = await import_junit(client, world.project.key, b"<testsuite><testcase")
    unknown_encoding = await import_junit(
        client, world.project.key, b'<?xml version="1.0" encoding="foo-bar"?><testsuites/>'
    )
    unknown_environment = await import_junit(client, world.project.key, read_fixture("jest.xml"), environment="Prod")
    unknown_suite = await import_junit(client, world.project.key, read_fixture("jest.xml"), suite="Nope")
    too_large = await import_junit(
        client, world.project.key, b"<testsuite>" + b" " * (10 * 1024 * 1024) + b"</testsuite>"
    )

    assert (bomb.status_code, read_code(bomb)) == (422, "JUNIT_INVALID")
    assert (external.status_code, read_code(external)) == (422, "JUNIT_INVALID")
    assert (broken.status_code, read_code(broken)) == (422, "JUNIT_INVALID")
    assert (unknown_encoding.status_code, read_code(unknown_encoding)) == (422, "JUNIT_INVALID")
    assert (unknown_environment.status_code, read_code(unknown_environment)) == (422, "UNKNOWN_REFERENCE")
    assert (unknown_suite.status_code, read_code(unknown_suite)) == (422, "UNKNOWN_REFERENCE")
    assert (too_large.status_code, read_code(too_large)) == (413, "FILE_TOO_LARGE")
    assert await count_runs(container, world.project.id) == 0


async def test_a_viewer_cannot_import(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_import_world(client, container, recording_mailer, role=ProjectRole.VIEWER)
    use_session(client, world.runner.account.session_token)

    response = await import_junit(client, world.project.key, read_fixture("jest.xml"))

    assert response.status_code == 403
    assert read_code(response) == "PERMISSION_DENIED"
