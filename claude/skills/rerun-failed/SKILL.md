---
name: rerun-failed
description: Re-run only the failed and blocked cases of a finished Tessio run in Claude in Chrome, at most 50 cases per run. Use when asked to re-run failures, retry a run or re-test what failed.
argument-hint: <run-id>
allowed-tools: mcp__plugin_tessio_tessio__*, mcp__claude-in-chrome__*, Bash(curl:*), Bash(mkdir:*)
---

# Re-run failed cases

Arguments: `$ARGUMENTS` = `<run-id>`.

A Claude suite run takes at most **50 cases**, as in `/tessio:run-suite`. A manual suite run has no such limit, so its re-run can have more than 50 failed cases. Those run as several runs of at most 50, one after the other.

1. Call `get_failed_cases(run_id)`. If the list is empty, say so and stop.
2. **Pick one run or several.**
   - A story run (the reply has `story_key`): one child run, step 3.
   - A suite run (the reply has `suite` instead, and each case its `story_key`) with 50 cases or fewer: one child run, step 3.
   - A suite run with **more than 50 cases**: call `get_suite_context(<suite>)` (`SUITE_ARCHIVED`: say the suite is archived and stop). Keep, in the order of the `get_failed_cases` reply, only the cases whose `case_id` is an `id` in `stories[].cases`; the server re-runs only those. Tell the user the codes of the other cases: a code in `skipped_cases` with its reason, any other code is no longer in the suite.
     - None left: say so and stop.
     - 50 or fewer left: one child run, step 3.
     - More than 50 left: several child runs, step 4.
3. **One child run, linked to the parent.** Start it with `environment` from the `get_failed_cases` reply. The server picks the parent's failed and blocked cases that are still runnable.
   - A story run: call `start_run(story_key, environment, parent_run_id=run_id)`.
   - A suite run: call `start_run(suite=<suite>, environment, parent_run_id=run_id)`.
   - If it is refused, see step 5 and stop.
   - Follow [../run-story-tests/references/execute-cases.md](../run-story-tests/references/execute-cases.md) for the new run.
4. **Several child runs of at most 50 cases.** `start_run` takes either `parent_run_id` or `case_ids`, never both (`INVALID_REQUEST`), so these runs pass `case_ids` and are not linked to the parent run in Tessio. Say so.
   1. **Split the kept cases into batches** of at most 50 cases, in that order, and tell the user: "N cases in B runs of at most 50."
   2. Run the batches one at a time. Start the next batch only after `finish_run` of the previous one, because a suite has one running run at a time.
   3. **Start each batch** with `start_run(suite=<suite id>, environment, case_ids=<the batch's case ids>)`: the suite `id` from the context, `environment` from the `get_failed_cases` reply.
      - `CASE_NOT_READY` or `UNKNOWN_REFERENCE` on a case: the suite changed. Call `get_suite_context` again, drop the cases no longer in `stories[].cases` from the batches not yet run, split them again, and retry the start once. If it is refused again, say why and go to step 4.5.
      - `UNKNOWN_REFERENCE` naming an environment ("No active environment named …"): it was archived. Call `get_suite_context` again, list its `environments` names, and ask the user which one to use for this batch and every later one, then retry the start.
      - Any other refusal: see step 5, then go to step 4.5.
   4. **Execute the run** with [../run-story-tests/references/execute-cases.md](../run-story-tests/references/execute-cases.md). In the `finish_run` summary, name the batch and the parent run ("Re-run 2 of 3 of the failed cases of run <run_id>"). If the health check finds the environment down, start no further batch and go to step 4.5. After `finish_run`, tell the user the run's status and its passed, failed and blocked counts per story, then start the next batch.
   5. **Stopping before the last batch:** say which runs finished and how many cases did not run, and give the command that runs the rest later: `/tessio:run-suite "<suite name>" <environment> <codes of the cases that did not run>`. Then stop.
   6. After the last batch, tell the user each run id with its status, and `/tessio:rerun-failed <run-id>` for each run with failed or blocked cases.
5. **If a start is refused:**
   - `OPEN_GAPS_BLOCK_RUN`: follow [../answer-gaps/references/when-gaps-block.md](../answer-gaps/references/when-gaps-block.md).
   - `SUITE_ALREADY_RUNNING`: another run of the suite is still in progress; say so. It must be finished first, and a run with no activity for 4 hours is aborted on its own.
   - `NO_FAILED_CASES_TO_RERUN`: no failed or blocked case of the run is still Ready; say so.
   - `PERMISSION_DENIED`: your role cannot start runs (Admin, QC and Dev can); say so.
