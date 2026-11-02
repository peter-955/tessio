---
name: run-suite
description: Run the Ready Tessio test cases of a regression suite in Claude in Chrome, at most 50 cases per run, and record the results in Tessio. Use when asked to run a suite, run the regression tests or run a Tessio suite by name.
argument-hint: <suite> [environment] [case codes]
allowed-tools: mcp__plugin_tessio_tessio__*, mcp__claude-in-chrome__*, Bash(curl:*), Bash(mkdir:*)
---

# Run a suite

Arguments: `$ARGUMENTS` = `<suite> [environment] [case codes]`. `<suite>` is the suite's name or id, as on the suite page in Tessio. A name with spaces is quoted: `/tessio:run-suite "Checkout regression" staging`.

A run takes at most **50 cases**. A larger suite runs as several runs, one after the other, because a suite has only one running run at a time.

## 1. Load the suite

1. **Read the arguments.**
   - The suite: the quoted text (`"..."` or `'...'`) when the arguments start with a quote, else the first word.
   - Each other word that looks like a case code (`TC-<n>`, any case) is a case code. Any other word is the environment.
2. Call `get_suite_context(suite)`.
   - `NOT_FOUND`: when the arguments were several unquoted words, call `get_suite_context` once more with the whole argument text as the name (a name with spaces typed without quotes) and read no environment or case codes. If it is still `NOT_FOUND`, say that no suite of the token's project has this name or id, point to the project's **Suites** page, and stop.
   - `SUITE_ARCHIVED`: say the suite is archived and stop.
   - `PERMISSION_DENIED`: your role cannot read the suite; say so and stop.
3. **Tell the user** the suite name, `case_count`, the number of stories, and the `skipped_cases` (code, title, `story_key`, and the reason: `not_ready` means the case is not Ready, `needs_review` means it is flagged *Needs review*). Skipped cases never run; QC fixes them in Tessio.
4. If `case_count` is 0, say there is no Ready case to run and stop.
5. **Pick the environment:** the argument (matched to an `environments` name without case), else the one with `is_default`, else the only environment, else ask the user. An argument that matches no environment: list the names and ask. Use the same environment for every run of the suite.
6. **List the cases to run.** Take the cases of `stories[].cases` in that order (stories in order, then each story's cases), with their `id` and `code`.
   - If case codes were given, keep only those, in the order given. Say which codes were dropped: a code in `skipped_cases` is skipped (give the reason), any other code is not in the suite. If no case is left, stop.
7. **Split the list into batches** of at most 50 cases, in that order, and tell the user: "N cases in B runs of at most 50."

## 2. Run each batch

Run the batches one at a time. Start the next batch only after `finish_run` of the previous one.

1. **Start the run.** Pass the suite `id` from the context, not the name, and the environment name.
   - One batch with every case of the suite (no case codes given, 50 cases or fewer): `start_run(suite=<suite id>, environment)` without `case_ids`. The run then keeps the skipped cases in its report.
   - Otherwise: `start_run(suite=<suite id>, environment, case_ids=<the batch's case ids>)`.
2. **If the start is refused:**
   - `OPEN_GAPS_BLOCK_RUN`: open gaps on stories of the suite block every run of it. The message lists the gaps with their story keys and assignees. Follow [../answer-gaps/references/when-gaps-block.md](../answer-gaps/references/when-gaps-block.md), then go to step 4 of this section.
   - `SUITE_ALREADY_RUNNING`: another run of this suite is still in progress, yours from an earlier session or someone else's. Say so: it must be finished first, and a run with no activity for 4 hours is aborted on its own. Go to step 4.
   - `CASE_NOT_READY` or `UNKNOWN_REFERENCE` on a case: the suite changed since you loaded it. Call `get_suite_context` again, rebuild the remaining batches from step 1.6, and retry the start once. If it is refused again, say why and go to step 4.
   - `UNKNOWN_REFERENCE` naming an environment ("No active environment named …"): the environment was archived since you loaded the suite. Call `get_suite_context` again, list its `environments` names, and ask the user which one to use. Use that environment for this batch and every later one, then retry the start. If the context has no environment left, say so and go to step 4.
   - `SUITE_EMPTY`: no Ready case is left; say so and go to step 4.
   - `INVALID_REQUEST` that asks you to pick an environment: ask the user, then retry.
   - `PERMISSION_DENIED`: your role cannot start runs (Admin, QC and Dev can); say so and stop.
3. **Execute the run** with [../run-story-tests/references/execute-cases.md](../run-story-tests/references/execute-cases.md). In a suite run each case of the `start_run` reply also has its `story_key`.
   - In the `finish_run` summary, name the batch ("Run 2 of 3 of suite Checkout regression"), the stories with failed or blocked cases, and, in the first run, how many cases the suite skipped.
   - If the health check finds the environment down, the procedure finishes the run with the reason. Start no further batch, and go to step 4.
   - After `finish_run`, tell the user the run's status and its passed, failed and blocked counts per story, then start the next batch.
4. **Stopping before the last batch** (gaps, a running run, the environment down, or the user asks to stop): say which runs finished and how many cases did not run. Give the command that runs the rest later: `/tessio:run-suite "<suite name>" <environment> <codes of the cases that did not run>`. Then stop.

## 3. Report

After the last batch, tell the user:

- per story: the passed, failed and blocked cases;
- the skipped cases from step 1.3;
- each run id with its status, and `missing_screenshots` if any (the hook retries them the next time it runs);
- for each run with failed or blocked cases: `/tessio:rerun-failed <run-id>` re-runs only those.

A suite run never changes a story's test status. Its failures open on each case's own story, as for a story run.
