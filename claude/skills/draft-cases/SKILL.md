---
name: draft-cases
description: Draft Tessio test cases from a Jira story's acceptance criteria, created as Draft for QC to review. Use when asked to write, draft, generate or suggest test cases for a story key.
argument-hint: <STORY-KEY>
allowed-tools: mcp__plugin_tessio_tessio__*
---

# Draft test cases from the acceptance criteria

Arguments: `$ARGUMENTS` = `<STORY-KEY>`.

1. Call `get_story_context(story_key)`. If the story has no active AC, say so and stop.
2. For each active AC, write:
   - one case for the behaviour the AC describes;
   - one more case for each failure, limit or edge case the AC itself names. Don't add cases the AC doesn't support.
3. Each case links the AC it covers in `criterion_codes`. Its `source` is that AC code, for example `AC2`.
4. Leave out a case when a Ready case in the context already covers the same behaviour.
5. Write steps a tester can follow without guessing: one action per step, each with an expected result. Use `{{data.<key>}}` for data the context lists. For data it doesn't list, name a new key and keep it for the summary.
6. Follow [../import-cases/references/create-cases.md](../import-cases/references/create-cases.md) from "Check" to the end. Its mapping rules about secrets and existing cases apply here too.
