# Create Draft cases in Tessio

Shared by `/tessio:import-cases` and `/tessio:draft-cases`.

## Case shape

Each case sent to `check_draft_cases` and `create_draft_cases`:

| Field | Rule |
| --- | --- |
| `story_key` | The Jira key, for example `SHOP-12`. |
| `title` | 1 to 200 characters. |
| `priority` | `critical`, `high`, `medium` or `low`. Leave it out when the source gives none: it becomes `medium`. |
| `business_value`, `preconditions` | Optional, up to 5000 characters each. |
| `steps` | 1 to 100 steps, in order: `{action, expected?}`, each text up to 5000 characters. |
| `criterion_codes` | AC codes like `AC2`. |
| `source` | Where the case came from, up to 200 characters. |

Send at most 100 cases per call. Split a bigger set story by story.

## Mapping rules

- **Keep the author's words.** Don't rewrite, translate, shorten or improve steps. Split a cell into steps only where the source numbers them or puts them on separate lines.
- **Never invent.** A step without an expected result keeps no `expected`. AC codes come only from the source when importing, or from the AC being drafted.
- **No secrets in case text.** Replace a password, token, API key or similar value with `{{data.<key>}}`, choosing a short key such as `admin_password`. Never send the value to Tessio, never write it in chat, and list the key in the summary.
- **Files.** A step that uploads a file keeps its words. QC attaches the file later on the case's Files tab.
- **Only create.** Never edit existing cases, Jira or test data.

## Check

1. Call `check_draft_cases(cases)`. The reply lists only the cases with an issue, by `index`:
   - `problem`: the case cannot be created. `story_not_found`, `too_many_steps` and `text_too_long` need a person, so leave the case out and list it. Fix only what the source makes clear, such as a story key with a typo that matches one story.
   - `is_duplicate`: a case with the same title exists on that story, or earlier in the list.
   - `unknown_criterion_codes`: these codes are not current AC of the story. They are not linked.
2. If you fixed a case, check again.

## Confirm

Show the user, before creating anything:

- for each story, the number of cases that will be created;
- the cases left out, each with its `source` and the reason;
- the duplicates, with their `source`;
- the unknown AC codes;
- the `{{data.<key>}}` keys that need a value in Test data.

Then ask: "Create {n} cases as Draft?" Leave duplicates out unless the user says to keep them. Create nothing without a yes.

## Create

1. Call `create_draft_cases(cases)` with only the confirmed cases. It returns the new codes in input order. If it refuses the call, nothing was created: check again and show the user what changed.
2. Report each story with its new codes, and the link `<tessio_url>/projects/<project key>/test-cases?storyKey=<STORY-KEY>` when you know the project key.
3. Remind the user that the cases are Draft: QC reviews each one and marks it Ready before it can run.
