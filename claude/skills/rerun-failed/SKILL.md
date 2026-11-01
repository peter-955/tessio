---
name: rerun-failed
description: Re-run only the failed and blocked cases of a finished Tessio run in Claude in Chrome. Use when asked to re-run failures, retry a run or re-test what failed.
argument-hint: <run-id>
allowed-tools: mcp__plugin_tessio_tessio__*, mcp__claude-in-chrome__*, Bash(curl:*), Bash(mkdir:*)
---

# Re-run failed cases

Arguments: `$ARGUMENTS` = `<run-id>`.

1. Call `get_failed_cases(run_id)`. If the list is empty, say so and stop.
2. Call `start_run(story_key, environment, parent_run_id=run_id)`, with `story_key` and `environment` from the `get_failed_cases` reply. The server picks the parent's failed and blocked cases.
3. Follow [../run-story-tests/references/execute-cases.md](../run-story-tests/references/execute-cases.md) for the new run.
