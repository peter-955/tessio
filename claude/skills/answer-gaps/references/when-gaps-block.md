# When open gaps block a run

Use this when a run cannot start because gaps are open:

- `get_open_gaps(story_key)` lists open gaps before the start, or
- `start_run` is refused with `OPEN_GAPS_BLOCK_RUN`: a story run, a re-run, or a suite run (`/tessio:run-suite`). Suite runs get the same code; there is no separate `GAPS_OPEN` code.

For a suite run, the blocked stories are every story with a case in the suite that has an open gap, skipped cases included. The refusal message lists up to 20 gaps, each as `<STORY-KEY> gap <gap id> (assigned to <name>, the <Role> role, or nobody): <question>`, separated by `; `.

- **The whole list:** the message does not end with "and N more". Its story keys are the blocked stories.
- **A cut-off list:** the message ends with "; and N more". Other blocked stories are not named. Take the candidates from the suite context (`get_suite_context(suite)`; call it now if you have no reply yet): every `stories[].key` plus every `skipped_cases[].story_key`, each once. Call `get_open_gaps(story_key)` for each candidate. A candidate with open gaps is a blocked story.

The message gives no severity, no target and no deactivated assignee, and cuts each question to 120 characters. Take those from the `get_open_gaps` and `get_my_gaps` replies, never from the message.

Don't start the run, and don't raise, answer or reassign gaps from here.

1. **List the gaps.** For each blocked story, use its `get_open_gaps(story_key)` reply, or call it now. The refusal message only tells you which stories are blocked. Each gap names who must answer it:
   - `assignee_name`: one person;
   - `assignee_role`: anyone in that role queue;
   - `is_assignee_deactivated`: the assignee left; the gap needs reassigning.
2. **Find the caller's gaps.** Call `get_my_gaps(story_key)` once per blocked story. For a suite run with more than three blocked stories, call `get_my_gaps()` once without a story key instead, and keep the gaps of the blocked stories. Its gap ids are the ones the caller can answer. `PERMISSION_DENIED` means none.
3. **Tell the user**, grouped by assignee, one line per gap (severity, target, question):
   - **Yours** first: the gaps from step 2.
   - Then each other person by name, and each role queue as "any BA", "any QC" and so on.
   - Then **Needs reassigning**: gaps whose assignee was deactivated.
   With several stories, group by story first.
4. **Offer** `/tessio:answer-gaps <STORY-KEY>` (or `/tessio:answer-gaps` for several stories) when the caller has gaps, and say that the run can start once every gap on the story is answered. A suite run can start once every gap on all of its blocked stories is answered.
5. **Name who must answer the rest.** They see their gaps under **My gaps** in Tessio, or in the story's **Gaps** tab, and can answer them there or with `/tessio:answer-gaps`. A gap that needs reassigning is reassigned on the story's **Gaps** tab (**Reassign**) by anyone who can answer gaps.
6. **Stop.** Once the gaps are answered, the person runs the same command again.
