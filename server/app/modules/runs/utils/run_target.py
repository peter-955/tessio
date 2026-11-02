from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_target.entity import RunTarget
from app.modules.runs.ports.run_story_reader import RunStoryReader


async def find_run_target(run: Run, run_story_reader: RunStoryReader) -> RunTarget:
    if run.test_suite_id is not None:
        return RunTarget(story_jira_key=None, suite_name=await run_story_reader.find_suite_name(run.test_suite_id))
    if run.story_id is None:
        return RunTarget(story_jira_key=None, suite_name=None)
    return RunTarget(story_jira_key=await run_story_reader.find_jira_key(run.story_id), suite_name=None)
