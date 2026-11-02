# Readable test cases: one sheet to follow while testing and reviewing

**Status:** Accepted, built on 2026-11-01 (what the code does is in the [runs spec, RUN-7, RUN-8 and RUN-12](../spec/runs.md#run-12-readable-case-sheet-wbs-3109-3610) and the [test-cases spec, CASE-12](../spec/test-cases.md#case-12-read-view-of-a-test-case-wbs-3610))
**Date:** 2026-11-01
**WBS:** [3.10.9](../wbs/wbs.md#310-runs) (readable case sheet in runs), [3.6.10](../wbs/wbs.md#36-test-cases) (read view of a test case)
**Related:** [runs spec, RUN-7 and RUN-8](../spec/runs.md#run-7-run-detail-and-live-progress-wbs-3102-3103) (run detail, manual run), [test-cases spec](../spec/test-cases.md), [environments and test data spec, DATA-5](../spec/environments-and-test-data.md#data-5-secrets-during-a-run-wbs-394) (secrets during a run), [user flows §3 and §4](../design/user-flows.md#3-a-claude-run)

## Decisions at a glance

| Area | Decision |
| --- | --- |
| Goal | A tester can run a case from **one screen**, and a Dev can read a case and its result without opening other pages. |
| Shared piece | One read-only **case sheet** shows a case the same way everywhere: AC, why it matters, preconditions, test data, steps. |
| Placeholders | `{{data.key}}` shows the **value for the environment** as a chip; the key is in the tooltip. A secret shows `••••`. A key with no value shows a warning chip. |
| Secrets in a manual run | Masked, with a **Reveal** button. Same rules and audit as Claude's `resolve_data`: `secret.use_in_run`, starter only, running run, audited as `secret.resolve` with the run id. |
| Manual recording | Case sheet on top, an environment bar with the base URL, steps with the **expected result as visible as the action**, evidence behind a small button. |
| Test case page | **Read view for everyone by default.** People who can edit press *Edit* to get today's form. |
| Run detail | Each case card gets a collapsed *Case details* part with preconditions and the data used in that run. |
| Server | The run detail returns the fixed version's business value, preconditions, AC and files, the environment base URL and the run's data. One new REST route for reveals. No new table. |
| Claude runs | Unchanged. Claude already gets all of this from `get_story_context` and `start_run`. |

## 1. Why

Checked on 2026-11-01 on the end-to-end stack, with a case whose preconditions and steps use `{{data.shopper_email}}`, `{{data.shopper_password}}` (a secret) and `{{data.saved_card_last4}}`.

**Manual recording** (`/projects/[projectKey]/runs/[runId]/record`):

- Each step shows only the action and "Expected: …" in small grey text. The expected result is what the tester checks against, but it is the faintest text on the screen.
- Preconditions, business value and linked AC are not shown. The server does not send them: `RunCaseResponse` holds only code, title, version and steps.
- The environment shows by name only. The tester has to find the base URL somewhere else.
- `{{data.shopper_email}}` is shown as raw text. The tester opens the Test data page in another tab to read the value, and has to find the right environment column there.
- Every step has a full-width dropzone for evidence. A 4-step case is about 2,000 px tall, mostly upload boxes.
- *Suggested: Passed* shows as soon as one step passes, while the other steps are still not marked. Saving then records them as Skipped.

**Test case page** (`/projects/[projectKey]/test-cases/[caseCode]`):

- Someone who cannot edit (Dev, PM, BA, Viewer) gets the edit form with every field disabled. The text is light grey on grey, and the AC field still says "Choose acceptance criteria".
- Placeholders are raw text here too.

**Run detail** (`/projects/[projectKey]/runs/[runId]`):

- The results timeline reads well: step, expected, actual, error, screenshot, and failures open by default.
- A Dev looking at a failure cannot see the preconditions or the data the tester used without opening the case. The case link opens the current version, not the version the run executed.

## 2. The case sheet

One read-only component, used by the three screens. It shows a case at one version, with data values for one environment.

```
TC-2 · Saved card is offered first for a returning shopper      High · v1
Covers  AC1 The saved card is offered at checkout

Why it matters
  Returning shoppers pay in one click, which lifts checkout conversion.

Before you start                                             (highlighted)
  Shopper [anna@shop.test] exists and has paid once with the card ending [4242].
  Cart holds at least one item.

Test data · Staging
  shopper_email      anna@shop.test        [copy]
  shopper_password   ••••••••              [Reveal]  (manual run only)
  saved_card_last4   4242                  [copy]

Steps
  1  Sign in as [anna@shop.test] with password [••••]
     Expected  The home page shows the shopper's first name
  2  ...
```

Rules:

- **Order:** what to check (AC), why, what must be true first, what data to use, then the steps. That is the order a tester needs them.
- **Preconditions** sit in a highlighted box, because a missed precondition is the most common reason for a false failure.
- **Steps** show the action and the expected result in the same size and colour, each with its own label. Long text wraps; nothing is cut off.
- **Placeholder chips:**
  - a known value shows in monospace, with the key in the tooltip and a copy button;
  - a secret shows `••••`; where reveal is allowed, the chip has a *Reveal* action;
  - a key with no value for this environment shows a warning chip "No value for `key` on Staging";
  - `{{file.key}}` shows the file name, with a download link where the screen allows it.
- **Empty parts are left out.** No "Business value: —".
- Business value is shown in full.

Where it lives: `client/src/components/case-sheet/`, next to the other shared components (`runs-table`, `status-badge`), because both the `test-cases` and `runs` modules use it. The placeholder parsing is one util, `split-references.util.ts`, that turns a text into text parts and reference parts. The editor's `reference-query.util.ts` stays as it is.

## 3. Screen by screen

### 3.1 Manual recording

```
Manual run · SHOP-1                                           [Finish run]
Staging  https://staging.shop.test [open] [copy]  ·  1 of 3 cases recorded

Cases          │  [case sheet: AC, why, before you start, test data]
TC-2 ●         │
TC-3 ○         │  Step 1  Sign in as [anna@shop.test] with password [•••• Reveal]
TC-4 ○         │  Expected  The home page shows the shopper's first name
               │  ( Passed | Failed | Blocked | Skipped )
               │  Actual result [ one line, grows as you type ]   [Attach evidence]
               │  ...
               │  Case result: Passed (2 steps not marked will be saved as Skipped)
               │                                                   [Save result]
```

- An **environment bar** under the title, with the base URL as a link that opens in a new tab, and a copy button.
- The **case sheet** sits above the steps. Its *Steps* part is replaced by the recorder rows; the rest is the same.
- **Step row:** the action, then "Expected" with the same weight, then the status buttons, then a one-line *Actual result* that grows. The *What went wrong* box still appears only for Failed or Blocked.
- **Evidence:** a small *Attach evidence* button. The dropzone opens after a click. An attached file shows with its name.
- **Suggested status:** when some steps are not marked, the line says how many will be saved as Skipped, before *Save result* is pressed. The rule itself (RUN-8 AC3) does not change.
- **Reveal:** pressing *Reveal* on a secret calls the new route (§4.3) and shows the value in that chip until the case is saved or the page is left. Every reveal is audited.

### 3.2 Test case page

- **Everyone sees the case sheet first** on the Details tab, with an environment picker above the test data. It starts on the project's default environment.
- People with `test_case.edit` see an **Edit** button. It switches to today's form (`TestCaseForm`); *Save* or *Cancel* switches back. A Deprecated case has no Edit button, as today.
- **Reveal** on this page uses the existing `POST /api/projects/{project_key}/test-data/{item_id}/reveal`, so only roles with `secret.reveal` (Admin, QC) see the button. Others see `••••`.
- The Files and History tabs do not change.

### 3.3 Run detail

- Each case card gets a **Case details** toggle, closed by default. It opens the case sheet without its steps, at the version the run executed, with the data values of the run's environment. Secrets are always masked here, because the run may be finished.
- **Steps in the timeline** render their placeholders as chips, using the same values.
- The case code links to the case at the version the run executed (`/test-cases/[caseCode]?tab=history&version=n`), so a Dev sees what was tested, not what was edited later.

## 4. Server changes

### 4.1 Run detail payload

`GET /api/projects/{project_key}/runs/{run_id}` (`RunDetailResponse`) gains:

| Field | Where it comes from |
| --- | --- |
| `environmentBaseUrl` | the run's environment `base_url` |
| `cases[].businessValue`, `cases[].preconditions` | the fixed `TestCaseVersion`, already loaded by `GetRunUseCase` |
| `cases[].criteria[]` (`code`, `text`) | the version's AC links, active AC only, as in `get_story_context` |
| `cases[].files[]` (`key`, `name`) | the version's file references |
| `data[]` (`key`, `kind`, `value`) | the effective entries for the run's environment (`select_effective_entries`), limited to the keys the run's cases use (`RunScopeReader.list_data_keys`). `value` is `null` for a secret. |

Secrets never travel in this payload. The rest is read-only data the caller can already see with `test_data.view` and `test_case.view`.

### 4.2 Test case page data

No server change. The page reads `GET /api/projects/{project_key}/test-data/effective?environmentId=` (all roles have `test_data.view`) and matches the keys in the case text.

### 4.3 Reveal during a manual run

`POST /api/projects/{project_key}/runs/{run_id}/resolve-data` with `{"keys": ["shopper_password"]}` returns `{"values": {…}, "unknownKeys": […]}`.

- Same use case as the MCP tool: `ResolveDataUseCase` gets a second entry point that takes a `project_key` and a session actor, next to `execute_in_token_project`.
- Same rules: `secret.use_in_run`, starter only (`RUN_NOT_OWNED`), running run only (`RUN_NOT_RUNNING`), only keys the run's cases use.
- Same audit: one `secret.resolve` event per key, with the run id.
- The route is under the runs module's `manual_router.py`, beside the other manual run routes.

## 5. Out of scope

- How Claude runs cases. Claude already gets preconditions, data references and files from `get_story_context` and `start_run`.
- Changing a saved result, keyboard shortcuts, and printing a case. They can come later if testers ask.
- The edit form itself (`TestCaseForm`, `DSStepEditor`) does not change.

## 6. Open points

1. **File download during a manual run.** `get_test_file` is MCP only. Assumed: add `GET /api/projects/{project_key}/runs/{run_id}/files/{key}` with the same rules and the same file-version record. Until then the chip shows the file name only.
2. **Reveal on the test case page for Devs.** Devs have `secret.use_in_run` but not `secret.reveal`, so they cannot reveal on the case page. Assumed: keep it that way; a Dev who needs the value runs the case through Claude or asks QC.
3. **Version link.** Built: `?tab=history&version=n` opens History comparing version n with the latest.

## 7. Build plan

| Step | Work | Checks |
| --- | --- | --- |
| 1 | Server: extend `RunDetailResponse` (§4.1), add the reveal route (§4.3), export OpenAPI, regenerate client types | `uv run pytest`, `mypy`, `lint-imports`; API tests for the new fields, secret never in the payload, reveal rules and audit |
| 2 | Client: `split-references.util.ts` and the `case-sheet` component | unit tests for the util (known, secret, missing, file) and the component |
| 3 | Client: manual recording (§3.1) | component tests; e2e `07-manual-run` still passes |
| 4 | Client: test case read view and Edit switch (§3.2) | e2e `05-test-case` updated to press Edit first |
| 5 | Client: run detail *Case details* and chips (§3.3) | component tests |
| 6 | Docs: runs spec RUN-7 and RUN-8, test-cases spec, user flows §4, translations (en, fr, vi) | |
