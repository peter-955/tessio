---
name: run-story-tests
description: Run the Ready Tessio test cases of a Jira story in Claude in Chrome and record the results in Tessio. Use when asked to test a story, run its test cases or run a Tessio run for a story key.
argument-hint: <STORY-KEY> [environment] [case codes]
allowed-tools: mcp__plugin_tessio_tessio__*, mcp__claude-in-chrome__*, Bash(curl:*), Bash(mkdir:*)
---

# Run story tests

Arguments: `$ARGUMENTS` = `<STORY-KEY> [environment] [case codes]`.

1. Call `get_story_context(story_key)`.
2. Call `get_open_gaps(story_key)`. If any gap is open, follow [../answer-gaps/references/when-gaps-block.md](../answer-gaps/references/when-gaps-block.md) and stop.
3. If the story has no Ready cases, say so and stop.
4. Pick the environment: the argument, else the only environment, else ask the user.
5. If case codes were given, map them to their case ids from the context.
6. Call `start_run(story_key, environment, case_ids?)`. If it is refused with `OPEN_GAPS_BLOCK_RUN` (a gap was raised meanwhile), follow [../answer-gaps/references/when-gaps-block.md](../answer-gaps/references/when-gaps-block.md) and stop.
7. Follow [references/execute-cases.md](references/execute-cases.md) for the run.
