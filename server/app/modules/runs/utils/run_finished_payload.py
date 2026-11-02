from app.modules.notifications import RunFinishedPayload, RunOutcome, SuiteRunFinishedPayload
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_target.entity import RunTarget


def build_run_finished_payload(
    run: Run, report: RunReport, target: RunTarget
) -> RunFinishedPayload | SuiteRunFinishedPayload | None:
    outcome = RunOutcome(run.status.value)
    if run.test_suite_id is not None and target.suite_name is not None:
        return SuiteRunFinishedPayload(
            run_id=run.id,
            test_suite_id=run.test_suite_id,
            test_suite_name=target.suite_name,
            outcome=outcome,
            passed_count=report.counts.passed,
            failed_count=report.counts.failed,
            blocked_count=report.counts.blocked,
        )
    if run.story_id is None or target.story_jira_key is None:
        return None
    return RunFinishedPayload(
        run_id=run.id,
        story_id=run.story_id,
        story_jira_key=target.story_jira_key,
        outcome=outcome,
        passed_count=report.counts.passed,
        failed_count=report.counts.failed,
        blocked_count=report.counts.blocked,
    )
