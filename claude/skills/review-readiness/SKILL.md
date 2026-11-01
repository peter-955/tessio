---
name: review-readiness
description: Review a Jira story, its acceptance criteria and its Tessio test cases for gaps, and file the new ones in Tessio. Use when asked whether a story is ready to test, to review readiness or to find gaps.
argument-hint: <STORY-KEY>
allowed-tools: mcp__plugin_tessio_tessio__*, mcp__claude-in-chrome__*, Bash(curl:*), Bash(mkdir:*)
---

# Review readiness

Arguments: `$ARGUMENTS` = `<STORY-KEY>`.

1. Call `get_story_context(story_key)` and `get_open_gaps(story_key)`.
2. Review the story, each acceptance criterion and each test case. Look for these gap types:
   - `missing_ac`: behaviour the story needs that no criterion covers.
   - `unclear_goal`: the story or a criterion cannot be checked as written.
   - `missing_step`: a case skips an action or has no expected result.
   - `missing_test_data`: a case needs a value or file that is not defined.
   - `other`: anything else that blocks testing.
3. For each gap set:
   - `severity`: `high`, `medium` or `low`.
   - `target_type`: `story`, `criterion` or `test_case`.
   - `target_ref`: the AC code, the case code, or `null` for the story.
   - `data_scope="environment"` when the missing data belongs to an environment.
4. Leave out gaps that are already open.
5. If there are new gaps, call `raise_gaps(story_key, gaps)` once with all of them, then report `is_ready` and `open_gap_count`.
6. If there are no new gaps, do not call `raise_gaps`; report readiness from `get_open_gaps`.
7. Never edit Jira or the test cases.
