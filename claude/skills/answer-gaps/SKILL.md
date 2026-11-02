---
name: answer-gaps
description: Answer the open Tessio gaps waiting for you (assigned to you or to your role queue) so that blocked stories can be tested again. Suggests answers with their sources, asks you to pick, and saves only what you confirm. Use when asked to answer, clear or work through gaps, or when a run is blocked by open gaps.
argument-hint: "[STORY-KEY | mine]"
allowed-tools: mcp__plugin_tessio_tessio__*, Read, Grep, Glob, AskUserQuestion
---

# Answer gaps

Arguments: `$ARGUMENTS` = `[STORY-KEY | mine]`. No argument, or `mine`, means every gap waiting for you in the token's project.

## Guardrails

- Nothing is saved without the person's confirmation (step 5).
- Every suggested answer names its source. When you find no source, say so and ask an open question. Never invent a business rule, a limit or a value.
- Never ask for a secret value (password, token, API key, private key, card security code, any credential), and never write one in chat or in an answer. For a secret, give the Test data page link (step 6).
- Never edit test cases, Jira, files or code. Product code is only read, to cite it.

## 1. Load the gaps

1. Call `get_my_gaps(story_key?)`, with the story key when one was given.
   - `NOT_FOUND`: the story is not in this token's project; say so and stop.
   - `PERMISSION_DENIED`: Viewers cannot answer gaps; say so and stop.
   - No gaps: say "Nothing is waiting for you" and show the stories from the reply, if any, with their open gap count. Stop.
   - `gap_count` above the number of gaps listed: say that the rest come in the next round (run the skill again).
2. Call `get_story_context(story_key)` once for each story in the reply. It gives the story title, the AC, the cases with their steps and data keys, the test data (secrets only as `{{data.key}}`), `missing_data_keys` and the environments.
3. **Product code.** Check with `Glob` whether the working directory holds product source code (for example `**/*.{ts,tsx,js,jsx,py,java,kt,go,rb,cs,php,swift}`, at most a quick look). If it does, you may search it with `Grep` and `Read` for the terms of each question (field names, messages, limits, flags) and cite `path:line`. If it does not, use only Tessio sources.
4. **Order and group.** Keep the reply's order (high severity first). Put related gaps next to each other: the same target, the same data key, or the same question in other words. Answer a group together when one answer covers all of it.

## 2. Prepare each gap

For each gap, prepare:

- **The question in plain words**, in one or two sentences, without Tessio jargon.
- **What it blocks**: its target (`target.ref` and the AC text, or the case title and the step), and that every run on the story waits for it (from `stories[].open_gap_count`).
- **Two or three suggested answers**, each with one source:
  - the story title or an AC (`AC2: "..."`);
  - an earlier answer from `similar_answers` (`SHOP-8, earlier answer`);
  - existing test data from the context (`test data key checkout.currency`), never a secret's value;
  - product code (`src/checkout/limits.ts:42`), only when step 1.3 found the product's code.
  Fewer suggestions are fine. A suggestion without a real source is not offered.
- For a `missing_test_data` gap, also the data to save: the key (one from `missing_data_keys` or the case's `data_keys`, else a new key following the case's `{{data.<key>}}` naming), the value, the kind (`endpoint` for a URL, else `variable`) and the scope (no environment for the whole project, or the environment's name when `data_scope` is `environment`). If the value is a secret, prepare no value: the answer says where the secret goes, and step 6 gives the link.

## 3. Ask with one key press

Use `AskUserQuestion`, with up to four gaps (one question each) per call. Each question has 2 to 4 options:

- the suggested answers first: a short label, and the full answer text with its source in the description;
- then **Not mine (reassign)** and **Skip** as two options, or as one **Not mine or skip** option when there are three suggestions;
- the prompt's own free-text choice is **Write my own**: say so in the question text.

When there is no suggestion, the question says "I found no source for this" and asks it openly; the options are **Not mine (reassign)** and **Skip**, and the person writes the answer in the free-text choice.

Follow-ups, each again with `AskUserQuestion`:

- **Not mine or skip**: ask "Reassign" or "Skip".
- **Reassign**: offer up to three targets: the role queue that fits the gap type (`missing_ac` and `unclear_goal` → BA, `missing_step` → QC, `missing_test_data` → QC, or Dev for environment data, `other` → Admin) and members from `assignees` with that role. The free-text choice takes another name or role. Only `assignees` members and the roles `admin`, `pm`, `ba`, `qc`, `dev` are valid.
- **A missing data value** (a suggestion without a value, or a free-text answer that names a key without its value): ask for the value, unless it is a secret.

## 4. Build the final answer

- A picked suggestion is used as written. A free-text answer is used as the person typed it; you may fix only obvious typos.
- An answer is at most 4000 characters.
- For a data gap, the answer names the key and the scope, for example "Added `checkout.card` for staging: 4242 4242 4242 4242".
- Note each case the answer suggests updating (a missing step, a changed expected result, a new data key) for step 7.

## 5. Confirm, then save

1. Show the whole batch before saving anything, one line per gap:
   - the answer: gap, final answer text;
   - the test data: `key = value`, kind, "All environments" or the environment;
   - the reassignment: gap → name, or "any <role>";
   - skipped gaps.
2. Ask with `AskUserQuestion`: **Save all**, **Change one**, **Cancel this batch**.
   - **Change one**: ask which gap, go back to step 3 for it, then confirm again.
   - **Cancel this batch**: save nothing from it and go on with the next batch.
3. On **Save all**, for each gap of the batch:
   - **Test data first:** `set_test_data(key, value, kind, environment?)`. The reply says `created`, `updated` or `unchanged`; mention `overridden_in` environments, whose own value still wins.
     - `PERMISSION_DENIED` (PM and BA cannot edit test data): still save the answer, and say a QC, Dev or Admin must add the value on the Test data page (step 6).
     - `INVALID_REQUEST` because the key is a secret: save no value; the answer points to the Test data page.
     - `NOT_FOUND` for the environment: ask again which environment, from the context's environments.
   - **Answer:** `answer_gap(gap_id, answer)`. Keep the reply's `open_gap_count` and `is_ready` for the story.
   - **Reassign:** `reassign_gap(gap_id, assignee_user_id)` or `reassign_gap(gap_id, assignee_role)`, exactly one of the two.
   - `GAP_NOT_OPEN` or `NOT_FOUND`: someone else answered or moved the gap meanwhile; say so and go on.
   - Any other error: show its code and message, keep that gap open and go on.

## 6. Secrets

When a gap needs a secret (or `set_test_data` says the key is a secret):

- do not ask for it, and do not suggest a value;
- give the link from the `get_my_gaps` reply, `test_data_url` (the project's Test data page), and say: add the secret there, as "Secret", under the key the case uses;
- offer to answer the gap with where the secret now lives (for example "Secret `login.password` is set for staging on the Test data page"), after the person says it is saved. A secret is added only by an Admin or QC.

## 7. Wrap up

Show, per story:

- the open gaps left (from the last `answer_gap` reply, else `stories[].open_gap_count`), and the ones you skipped;
- whether runs are unblocked (`is_ready`). For a ready story, offer `/tessio:run-story-tests <STORY-KEY>`. For a story still blocked by gaps of other people, follow [references/when-gaps-block.md](references/when-gaps-block.md) to name who must answer them;
- the cases the answers suggest updating, with what to change. QC edits them in Tessio; this skill doesn't.
