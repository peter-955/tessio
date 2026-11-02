# Test cases

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.6 · Story prefix CASE · Index: [README](README.md)

## Purpose

Test cases replace the Google Sheet. Each case belongs to one story, covers one or more of its AC, has numbered steps with expected results, may reference test data and files, and goes through a review before it can run. Every save adds a version, and every run records the version it ran. Server: [server/app/modules/test_cases](../../server/app/modules/test_cases). Client: [client/src/modules/test-cases](../../client/src/modules/test-cases).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List, open, versions, file versions, download files | `test_case.view`, `file.download` | all |
| Create, edit, change status, mark reviewed, attach files, import | `test_case.edit` | Admin, QC |
| Upload an import file | `test_data.edit` (upload kind `import`) | Admin, QC, Dev |
| MCP `check_draft_cases`, `create_draft_cases` (Claude imports or drafts cases) | `test_case.edit` | Admin, QC |
| Read review comments | `test_case.view` | all |
| Add and resolve review comments | `test_case.edit` | Admin, QC |
| List labels, filter the case list by label | `test_case.view` | all |
| Create, rename, recolour and delete labels; set a case's labels | `test_case.edit` | Admin, QC |
| See flaky, disagreement and quarantine flags; filter by them; read the quarantine history | `test_case.view` | all |
| Quarantine a case and take it out of quarantine | `test_case.quarantine` | Admin, QC |
| List and open shared steps, see where a shared step is used | `test_case.view` | all |
| Create, edit and archive shared steps; set a case's parameters and data rows | `test_case.edit` | Admin, QC |

Without `test_case.edit` the editor is read-only ("You can view this case but not edit it."). The new-case page says "You can't create test cases".

## User stories

### CASE-1 Test case list (WBS 3.6.1)

As a QC, I want all cases of the project with filters, so that I find the ones I need.

- AC1: `/projects/[projectKey]/test-cases` lists code, title, story, priority, status, step count, AC count, last saved, a Needs review mark and the latest result.
- AC2: Filters: story (`storyKey`), status, priority, acceptance criterion (`criterionId`, needs a story first), "Needs review only" (`needsReview`), labels (`label`, repeatable, CASE-13 AC7), flaky, disagreeing and quarantined (`flaky`, `disagreeing`, `quarantined`, each `true` or `false`, CASE-14 AC8), and search by code or title (`query`, up to 100 characters).
- AC3: The story detail has a Test cases tab with the same list for that story.
- AC4: With no cases: "No test cases yet. Write a case for a story, or import cases from a spreadsheet." With filters and no match: "No cases match these filters."

### CASE-2 Write a test case (WBS 3.6.2)

As a QC, I want to write a case with business value, preconditions, steps and expected results, so that anyone can run it the same way.

- AC1: "New test case" (`/projects/[projectKey]/test-cases/new`) posts to `POST /api/projects/{project_key}/test-cases` with the story key, title (1 to 200 characters), priority (`critical`, `high`, `medium` by default, `low`), business value and preconditions (each up to 5000), steps and AC links.
- AC2: A step has an action (1 to 5000 characters) and an optional expected result (up to 5000). A case has at most 100 steps; steps can be added, moved up or down, and removed. The editor shows the steps on the numbered timeline of [RUN-12 AC5](runs.md#run-12-readable-case-sheet-wbs-3109-3610), each step's fields in a box with its menu (Move up, Move down, Remove).
- AC3: The case gets the next code of the project, `TC-<n>` (TC-1, TC-2…), and starts as `draft`. Codes never repeat in a project.
- AC4: A case belongs to exactly one story.
- AC5: `/projects/[projectKey]/test-cases/[caseCode]` opens the editor; the code is matched without case.

### CASE-3 Link cases to AC (WBS 3.6.3)

As a QC, I want to link a case to the AC it covers, so that coverage is visible.

- AC1: "Covers acceptance criteria" offers the story's current AC; a case may link up to 50.
- AC2: Linking an AC of another story, or a removed AC that was not linked before, gets `INVALID_REQUEST` ("Link only current acceptance criteria of this story."). A removed AC that was already linked stays linked and shows "(removed)".
- AC3: One AC can be covered by many cases, and one case can cover many AC.

### CASE-4 Test data references (WBS 3.6.4)

As a QC, I want to insert `{{data.key}}` in steps, so that the value is kept once in Test data.

- AC1: Typing `{{data` or `{{file` in preconditions or a step shows matching keys ("References").
- AC2: A reference is `{{data.<key>}}` or `{{file.<key>}}`, where the key starts with a letter and uses letters, digits, `_`, `.` or `-` (at most 100 characters).
- AC3: A data reference is known when the key exists in the project's test data, in any scope.

### CASE-5 Test case files (WBS 3.6.4b)

As a QC, I want to attach files that steps use, so that Claude and testers upload the right sample.

- AC1: The Files tab uploads a file through the signed upload flow (kind `test_file`, up to 20 MB, the project's allowed types) and attaches it with a key: `POST /api/projects/{project_key}/test-cases/{case_code}/files`.
- AC2: Keys are unique per case. Steps use them as `{{file.<key>}}`.
- AC3: Uploading again under the same key adds a new file version. Each attach adds a new case version, so a run knows which file version it used.
- AC4: "Versions" lists a key's file versions (`GET …/files/{file_key}/versions`); "Download" gets a 5-minute link.
- AC5: A file of another kind gets `INVALID_REQUEST` ("Upload the file as a test file."); a file not uploaded yet gets `UPLOAD_NOT_COMPLETED`; a file already attached to a case gets `CONFLICT`.

### CASE-6 Review workflow (WBS 3.6.5)

As a QC, I want cases to go through Draft, In review and Ready, so that only reviewed cases run.

- AC1: Status changes use `PUT /api/projects/{project_key}/test-cases/{case_code}/status` with the transitions in the Rules table. Buttons: Submit for review, Mark ready, Back to draft, Back to review, Deprecate, Restore to draft.
- AC2: Ready needs at least one step (`CASE_NOT_READY`) and every `{{data.…}}` and `{{file.…}}` reference to exist (`UNKNOWN_REFERENCE`, listing the unknown ones).
- AC3: Any Admin or QC may mark a case Ready, including the author, unless the project turns on "Reviewer must not be the author" (CASE-15 AC6). An open review comment blocks Ready (CASE-15 AC4).
- AC4: Editing keeps the status. Editing a Ready case runs the Ready checks on the new version.
- AC5: A `deprecated` case cannot be edited (`CONFLICT`, "Restore the test case to Draft before editing it.") and is left out of runs and coverage. Deprecate asks "Deprecate {code}?".
- AC6: Only `ready` cases can run ([runs.md](runs.md)).

### CASE-7 Version history (WBS 3.6.6)

As a QC, I want every save kept, so that I can see what changed and which version a run used.

- AC1: `PATCH /api/projects/{project_key}/test-cases/{case_code}` sends the changes with `baseVersionNumber`. A save adds version n+1; versions are never changed. A save with no real change adds nothing.
- AC2: If someone saved meanwhile, the save gets `CONFLICT` ("Someone saved a newer version. Reload to see it.").
- AC3: The History tab lists versions (`GET …/versions`) with who saved them, and "Compare versions" shows field and step differences. A version that changes the parameters or data rows (CASE-16 AC8) shows a "Parameters and data rows" entry: the parameter names, then one numbered line per data row ("1. value | value"), with the changed words marked, so such a version never shows as "These versions are identical."
- AC4: A run fixes each case's version when it starts; the run detail shows "v{number}".
- AC5: `?tab=history&version=n` opens History comparing version n with the latest (the link from a run, RUN-7 AC8).

### CASE-8 AC changed, review (WBS 3.7.4)

As a QC, I want cases flagged when their AC change in Jira, so that I re-check them.

- AC1: When a sync changes or removes an AC, every linked case that is not `deprecated` gets the Needs review flag, with the changed AC codes.
- AC2: The editor shows "Acceptance criteria changed since the last review: {codes}".
- AC3: "Mark reviewed" (`POST …/review`) clears the flag. Marking the case Ready clears it too.

### CASE-9 Import from a spreadsheet (WBS 3.6.7)

As a QC, I want to import the existing sheet, so that I don't retype every case.

- AC1: "Import" takes an `.xlsx` (one tab per story, tab name = Jira key) or a `.csv` with a Story column, up to 5 MB. The file is uploaded with kind `import`, and only the person who uploaded it can preview or commit it.
- AC2: `POST /api/projects/{project_key}/test-case-imports/preview` lists the cases found, with location, story, title, priority, step count, AC and notes. Rows with a problem are shown but cannot be picked: No story key, Story not found, Too many steps, Text too long. A title already used on that story is marked Duplicate. Skipped parts are listed (Step without a case, Sheet without a header row). Unknown AC codes are listed.
- AC3: Recognised headers (any case): Story (or "Story key", "Jira key"), Title ("Test case", "Name"), Priority, Business value, Preconditions, Step ("Steps", "Action"), Expected ("Expected result"), Covers AC ("AC", "Acceptance criteria"). AC codes like `AC2`, `AC-2` or `AC 2` are read.
- AC4: `POST /api/projects/{project_key}/test-case-imports/commit` creates the chosen cases (up to 500) as `draft`, linking the AC that exist.
- AC5: A file that cannot be read gets `IMPORT_INVALID_FILE`; a file over 5 MB gets `FILE_TOO_LARGE`; a choice that is not importable gets `INVALID_REQUEST`.

### CASE-10 Claude imports cases from any file (WBS 3.6.9, 5.8, 5.9)

As a QC, I want Claude to read our test plan in whatever shape it is, so that I don't have to reformat it for the import.

Design record: [Claude drafts test cases proposal](../discussions/claude-drafts-cases-proposal.md). Claude side: [claude/skills/import-cases](../../claude/skills/import-cases/SKILL.md).

- AC1: `/tessio:import-cases <file> [STORY-KEY]` in Claude Code reads `.xlsx` and `.docx` through `claude/scripts/extract_file.py` (standard library only, up to 5 MB and 5000 rows), and `.csv`, `.txt`, `.md`, `.pdf` and images directly.
- AC2: MCP `check_draft_cases(cases[])` takes 1 to 100 cases (story key, title, priority, business value, preconditions, 1 or more steps, AC codes, and a `source` of up to 200 characters) and creates nothing. It runs the same checks as the import preview (CASE-9 AC2) and returns `case_count`, `creatable_count`, and only the cases with an issue: `index`, `source`, `problem`, `is_duplicate`, `unknown_criterion_codes`.
- AC3: MCP `create_draft_cases(cases[])` creates every case as `draft`, version 1, authored by the token owner. It links the AC that exist and returns the new codes in input order. If any case has a problem, it refuses the whole call with `INVALID_REQUEST`, naming the indexes, and creates nothing. Duplicates are created.
- AC4: Story keys are upper-cased. AC codes like `AC2`, `ac-2` or `AC 2` are read as `AC2`; any other code is kept and reported as unknown. A blank expected result, business value or preconditions is stored as empty.
- AC5: The skill shows a summary (cases per story, cases left out, duplicates, unknown AC, `{{data.key}}` placeholders that need a value) and creates nothing until the user says yes. A secret found in the file is replaced with `{{data.<key>}}` and never sent to Tessio.

### CASE-11 Claude drafts cases from the AC (WBS 3.6.8)

As a QC, I want Claude to draft cases from a story's AC, so that I start from a reviewed list instead of a blank page.

- AC1: `/tessio:draft-cases <STORY-KEY>` reads the story with `get_story_context`, writes one case per active AC plus one for each failure or edge case the AC names, links the AC it covers, and sets `source` to that AC code. It leaves out behaviour a Ready case already covers.
- AC2: It then checks, confirms and creates with `check_draft_cases` and `create_draft_cases`, exactly as CASE-10 AC2 to AC5.

### CASE-12 Read view of a test case (WBS 3.6.10)

As a Dev, PM, BA or tester, I want to read a case as a document, so that I can follow its steps and data without a greyed-out form.

- AC1: The Details tab opens on the case sheet ([RUN-12](runs.md#run-12-readable-case-sheet-wbs-3109-3610)) with its steps as a numbered vertical timeline (RUN-12 AC5), for everyone. "Values from" picks the environment; it starts on the project default, else the first active environment. Values come from `GET /api/projects/{project_key}/test-data/effective?environmentId=`.
- AC2: People who can edit the case (`test_case.edit`, project not archived, case not Deprecated) see "Edit", which switches to the form. "Save" or "Cancel" switches back; Cancel drops unsaved changes.
- AC3: A secret shows `••••`. Roles with `secret.reveal` (Admin, QC) get Reveal, which uses `POST …/test-data/{item_id}/reveal` and its audit; others see "Hidden".

### CASE-13 Labels (WBS 9.1)

As a QC, I want to tag cases with labels such as `smoke` or `checkout`, so that I can find and group them across stories (and later build suites from them).

Design record: [competitive features proposal F1](../discussions/competitive-features-proposal.md#f1-regression-suites-test-plans-and-labels-l-wbs-91). Server: [server/app/modules/labels](../../server/app/modules/labels) (labels and their links) and [set_test_case_labels.py](../../server/app/modules/test_cases/usecases/set_test_case_labels.py) (a case's labels).

- AC1: A label belongs to one project and has a name and a colour. `GET /api/projects/{project_key}/labels` lists them by name (case-insensitive) with `id`, `name`, `color`, `caseCount` (how many cases carry it) and `createdAt`.
- AC2: `POST …/labels` creates a label from `name` (trimmed, 1 to 40 characters) and `color` (`gray` by default). Colours are a fixed palette: `gray`, `red`, `orange`, `yellow`, `green`, `teal`, `blue`, `violet`. Names are unique in a project without regard to case: a second "SMOKE" next to "Smoke" gets `CONFLICT` ("A label with this name already exists."). The same name may exist in another project.
- AC3: `PATCH …/labels/{label_id}` renames and/or recolours (each field optional). Renaming to another label's name gets `CONFLICT`; changing only the case of its own name is allowed. A save with no change publishes nothing.
- AC4: `DELETE …/labels/{label_id}` (204) deletes the label and removes it from every case. Nothing blocks the delete: a suite keeps no filter ("Add by filter" adds a fixed list of cases once, [SUITE-3](suites-and-plans.md#suite-3-add-cases-by-filter-wbs-91)), so the suites keep their cases.
- AC5: `PUT /api/projects/{project_key}/test-cases/{case_code}/labels` with `{"labelIds": [...]}` replaces the case's labels (at most 20 ids in the request, repeats included; a repeated id is stored once) and returns them as `[{id, name, color}]`, sorted by name. A label of another project, or an unknown id, gets `INVALID_REQUEST` ("Use only labels of this project.") and changes nothing. Labels are not versioned: setting them adds no case version and works in any status, Deprecated included.
- AC6: The case detail (`GET …/test-cases/{case_code}` and every route that returns it) and each row of the case list carry `labels: [{id, name, color}]`, sorted by name.
- AC7: The case list takes `label=<name>`, repeatable (up to 20). A case matches when it carries every named label; names are matched without case and trimmed, and an unknown name matches nothing. It combines with the other filters (CASE-1 AC2).
- AC8: MCP `get_story_context` lists each Ready case's label names as `labels` (left out when the case has none), so Claude can report or pick by label.
- AC9: Live events: creating, renaming, recolouring or deleting a label publishes `label.changed` (`ids.labelId`); changing a case's labels publishes `test_case.changed`. Neither is published when nothing changed.
- AC10: Screens ([client/src/modules/labels](../../client/src/modules/labels), strings in the `labels` namespace). The label manager card in project settings is [SET-5](settings.md#set-5-labels-wbs-91).
  - **Case list:** each row shows its labels as chips under the title. A "Labels" filter (a multi-select of the project's labels, hidden while the project has no labels and none is chosen) puts one `label=<name>` per chosen label in the URL and in the list query. Names read from the URL are trimmed, repeats are dropped without regard to case, and at most 20 names of at most 40 characters are kept; a name is shown in the label's own case.
  - **Case page, Details tab:** a "Labels" box above the case sheet shows the chips, or "No labels". With `test_case.edit` on a project that is not archived, "Edit labels" opens the picker in any status, Deprecated included: a multi-select of the project's labels (at most 20, "A case can have at most 20 labels."), a "New label" field with "Create and add", and Save labels / Cancel.
  - **Create by name:** "Create and add" creates the label in `gray` (`POST …/labels`) and adds it to the choice. A name that a label already has, in any case, picks that label without a request. An empty or too long name, or the server's `CONFLICT`, shows on the field.
  - **Save:** "Save labels" sends one `PUT …/test-cases/{case_code}/labels` with the chosen ids and shows "Labels saved" after the save; nothing is sent when the choice did not change. The labels are not part of the case form and add no version.
  - **Colours:** each palette colour is a design-system badge colour; `DSBadge` has `orange`, `teal`, `blue` and `violet` besides `gray`, `red`, `yellow` and `green`, each with an AA text token `--color-<colour>-text`.
  - **Refresh:** `label.changed` refetches the labels list, the case list and the case detail. Saving a case's labels refetches the labels list (case counts) and the case list for the person who saved.
  - **New case page:** has no picker; labels are added on the case page once the case exists.

### CASE-14 Flaky cases and quarantine (WBS 9.13)

As a QC, I want Tessio to tell me which cases pass and fail at random, and which ones a person and Claude see differently, so that I fix or quarantine them instead of chasing false failures.

Design record: [competitive features proposal F13](../discussions/competitive-features-proposal.md#f13-flaky-cases-and-quarantine-s-wbs-913). Server: [recompute_flaky.py](../../server/app/modules/test_cases/usecases/recompute_flaky.py), [flaky_case.py](../../server/app/modules/test_cases/utils/flaky_case.py) (the rules), [quarantine_test_case.py](../../server/app/modules/test_cases/usecases/quarantine_test_case.py), [release_test_case_quarantine.py](../../server/app/modules/test_cases/usecases/release_test_case_quarantine.py). Case results are read through the `CaseResultHistoryReader` port, which the runs module implements ([postgres_case_result_history_reader.py](../../server/app/modules/runs/infrastructure/postgres_case_result_history_reader.py)).

- AC1 (flaky): a case is flaky when its last 10 decisive results (`passed` or `failed`; `blocked` and `skipped` are ignored) on its **current version** have 3 or more pass↔fail flips, across all executors. `flakyScore` is the number of flips in that window (0 to 9). `flakySince` is the time the case first crossed 3 flips and stays while it is flaky; when it drops below 3 flips, `isFlaky` is false and `flakySince` is cleared. Two or three results can never make a case flaky (at most 1 or 2 flips).
- AC2 (new version resets): saving a new case version (an edit or a file attach) resets `flakyScore` to 0 and clears `flakySince` and the disagreement at once. Results on older versions never count.
- AC3 (disagreement): a case disagrees when, on its current version, the latest manual decisive result and the latest automated decisive result differ (one passed, one failed) and were recorded at most 24 hours apart. Automated means any executor other than `manual` (today `claude`; later `script` and `ci`). `disagreedAt` is the later of the two times; it is cleared when a newer result makes them agree or more than 24 hours apart.
- AC4 (when it is computed): after each recorded case result, MCP or manual ([RUN-4 AC7](runs.md#run-4-record-a-case-result-wbs-3102-3103)), job `test_cases.recompute_flaky` runs `RecomputeFlakyUseCase` for that case on the `maintenance` queue. A nightly job schedule `test_cases.sweep_flaky` (`45 3 * * *`, UTC) recomputes every case. The recompute locks the case row, stores `flaky_score`, `flaky_since` and `disagreed_at`, and publishes `test_case.changed` only when something changed. A job with a missing or invalid `testCaseId` is logged and dropped.
- AC5 (quarantine): `PUT /api/projects/{project_key}/test-cases/{case_code}/quarantine` with `{"reason"?: string}` (trimmed, up to 500 characters; blank means no reason) puts the case in quarantine and records who, when and why. `DELETE …/quarantine` takes it out. Both need `test_case.quarantine` (Admin, QC), return the case detail, and work in any status. Quarantining a quarantined case, or releasing a case that is not quarantined, changes nothing (the first reason and time stay) and returns 200.
- AC6 (auto-release): during a recompute, a quarantined case whose 10 most recent decisive results recorded after `quarantinedAt` are all `passed` leaves quarantine. Results from before the quarantine do not count; one failure among those 10 keeps it.
- AC7 (history): `GET …/test-cases/{case_code}/quarantine-events` (`test_case.view`) lists the quarantine history, newest first: `id`, `kind` (`quarantined`, `released`, `auto_released`), `actorId`, `actorName` (both null for `auto_released`), `reason` (only on `quarantined`), `createdAt`. A no-op PUT or DELETE adds no event.
- AC8 (where it shows): the case list rows carry `isFlaky`, `flakyScore`, `isDisagreeing`, `isQuarantined` and `quarantinedAt`; the case detail (and every route that returns it) also carries `flakySince`, `disagreedAt`, `quarantinedBy` and `quarantineReason`. `GET …/case-latest-results` carries `isFlaky`, `isDisagreeing` and `isQuarantined` per case. The case list filters `flaky`, `disagreeing` and `quarantined` take `true` or `false` and combine with the other filters (CASE-1 AC2).
- AC9 (what quarantine does today): nothing in runs. Until script runs exist (W13.T4), a quarantined case still runs, still opens failures and still fails a run; quarantine is a flag with a history. Insights (F5) uses these flags later.
- AC10 (live events): quarantine, release, auto-release and a recompute that changes the flags publish `test_case.changed`.
- AC11 (screens): strings live in the `flakyCases` namespace; icons `flaky` and `quarantine` ([client/src/modules/test-cases](../../client/src/modules/test-cases), components `flaky-case-*` and `quarantine-*`).
  - Case list: the Status cell shows a "Flaky" (yellow), "Disagreeing" (red) or "Quarantined" (gray) badge for each flag that is set, next to "Needs review". The filter bar has three checkboxes, "Flaky only", "Disagreeing only" and "Quarantined only". Each one sends `flaky=true`, `disagreeing=true` or `quarantined=true` and is kept in the page URL under the same name. The screen never sends `false`; the API still accepts it. A checked box counts as a filter for "No cases match these filters" and Clear filters.
  - Case detail header: the same badges after the priority badge. Users with `test_case.quarantine` on a project that is not archived (Admin, QC) get a "Quarantine" button, or "Release quarantine" when the case is quarantined, before the status actions. The button is shown in any case status and with unsaved edits.
  - Quarantine dialog: "Quarantine {code}?" with an optional Reason box (up to 500 characters). A blank reason sends `{}`, otherwise the trimmed `reason`. Success toasts: "{code} is in quarantine." and "{code} is out of quarantine." Release takes effect at once, with no confirmation.
  - Case detail alerts (under the existing alerts, for every role):
    - "In quarantine": since when, by whom (the member's name, or "a former member"), the reason if there is one, and a note that quarantine changes nothing in runs yet and ends after 10 passes in a row.
    - "Flaky case": `flakyScore` flips in the last 10 results on this version, and `flakySince`.
    - "A person and Claude disagree": `disagreedAt`.
  - History tab: below the versions, a "Quarantine history" timeline from `GET …/quarantine-events`, newest first: "Quarantined by {name}" with the reason, "Released by {name}", or "Released after 10 passes in a row". It is hidden when the case has no events.
  - Refresh: after quarantine or release, the screen stores the returned detail and refetches the case list, `case-latest-results` and the quarantine history. `test_case.changed` also refetches the quarantine history.

### CASE-15 Version compare and review comments (WBS 9.3)

As a QC reviewer, I want to compare two versions of a case and leave comments on it, so that the author fixes what I found before the case is Ready.

Design record: [competitive features proposal F3](../discussions/competitive-features-proposal.md#f3-version-compare-and-review-comments-s-wbs-93).

- AC1: *Compare versions* picks any two versions of the case and shows their fields and steps side by side, with changed lines highlighted. It reads the existing `GET …/test-cases/{case_code}/versions`, which returns every version in full (title, priority, business value, preconditions, steps, AC ids, data keys, file version ids, `createdBy`, `createdAt`), newest first. The server has no compare route.
- AC2: `GET /api/projects/{project_key}/test-cases/{case_code}/review-comments` lists every comment of the case, open and resolved, oldest first. Each has `id`, `versionId`, `versionNumber`, `stepOrder` (null for the whole case), `body`, `authorId`, `authorName`, `createdAt`, `isResolved`, `resolvedAt`, `resolvedBy` and `resolvedByName`.
- AC3: `POST …/review-comments` adds a comment with `body` (1 to 5000 characters, trimmed), an optional `stepOrder` (1 to 100) and an optional `versionNumber` (default: the current version). The step must exist in that version (`INVALID_REQUEST`, "Comment on a step of this version."); an unknown version number gets `NOT_FOUND` ("Test case version not found."). A deprecated case takes no comments (`CONFLICT`, "Restore the test case to Draft before commenting on it."). The reply is the new comment (201).
- AC4: While a comment of the case is open (on any version), moving the case to Ready is refused with `REVIEW_COMMENTS_OPEN` (409, "Resolve the open review comments ({n}) before marking the case Ready."). Other status moves, edits, and a case that is already Ready are not affected: adding a comment to a Ready case leaves it Ready.
- AC5: `PUT …/review-comments/{comment_id}/resolve` resolves a comment and records who and when. Any Admin or QC may resolve any comment, including their own. Resolving a resolved comment changes nothing and returns it as it is. A comment id of another case, or unknown, gets `NOT_FOUND` ("Review comment not found."). Comments are never edited, reopened or deleted.
- AC6: Project setting "Reviewer must not be the author" (`requireSeparateReviewer` on `PATCH /api/projects/{project_key}`, default off, [SET-4](settings.md#set-4-reviewer-must-not-be-the-author-wbs-93)). When it is on, the person who saved the case's current version cannot mark the case Ready or "Mark reviewed" (CASE-8 AC3): both get `REVIEWER_IS_AUTHOR` (403, "This project needs a reviewer who did not write the version under review."). Anyone else with `test_case.edit` can. The rule looks only at the current version's `createdBy`: if a reviewer edits the case, the reviewer becomes its author and the first author may then review it. Submit for review, Back to draft, Back to review and Deprecate stay open to the author.
- AC7: Adding or resolving a comment publishes `review_comment.changed` with `testCaseId`, `code`, `storyId` and `commentId`. The case list and case detail refetch on it, and so does the comment list (`GET_REVIEW_COMMENTS_KEY`).
- AC8: The case detail has two more tabs, **Review** (with the open comment count) and **Compare** (`?tab=review`, `?tab=compare`). The client code is in `client/src/modules/case-review/`; its strings are in the `caseReview` namespace.
- AC9: *Compare* ("Compare versions side by side") has two pickers, "From version" and "To version", which start on the previous and the current version and accept any two versions. A table shows, per row, the title, business value, preconditions, priority and each step, with the From version on the left and the To version on the right. The column headers name each version, who saved it and when. A changed row has a "Changed" badge and a coloured edge on both cells, and inside it the removed words are struck through on the left and the added words underlined on the right. A step only in the To version is "Added" (the left cell says "Not in this version"), and one only in the From version is "Removed". When either version has parameters, a "Parameters and data rows" row (after priority) shows each version's parameter names and numbered data rows, and counts as a change when they differ; with no difference anywhere the line says "These versions have the same fields, steps and data rows." Steps are lined up by content, so a step inserted in the middle shows as one added row, and a moved step shows "Step 2 → 3". "Show only changes" hides the rows that are the same, and a line counts the changes. With one version the tab says "Only one version so far. Compare two versions after the next save." AC links, data keys and files are not in this table; the History tab's compare (CASE-7 AC3) still lists them.
- AC10: *Review* shows, for Admin and QC, a form ("Comment on": "The whole case" or "Step n · action", then the comment, up to 5000 characters) that posts on the current version; an empty comment gets "Write a comment first." Below it are "Open comments (n)" and "Resolved (n)". Each comment shows its author, date, "The whole case" or "Step n", and its version ("Version n", or "On version n" in yellow for an older one); a resolved one adds "Resolved by {name}, {date}". Admin and QC get "Resolve" on each open comment. Other roles only read. A deprecated case shows "This case is deprecated. Restore it to Draft to add comments." and no form; open comments can still be resolved.
- AC11: While the case is In review and a comment is open, the detail shows "{n} review comments are open. Resolve them before marking the case Ready." (singular for one) with "Show comments" (opens the Review tab), and *Mark ready* is disabled with the title "Resolve the open review comments first.".
- AC12: With "Reviewer must not be the author" on, the person who saved the current version (the signed-in user's id equals `currentVersion.createdBy`) sees no *Mark ready* and no *Mark reviewed*, and, while the case is In review or needs review, the note "You saved version n, and this project needs a different reviewer. Another QC or Admin must mark the case Ready or reviewed.". The server still refuses with `REVIEWER_IS_AUTHOR` (AC6) if the call is made anyway.

### CASE-16 Shared steps and data-driven cases (WBS 9.2)

As a QC, I want to write a common sequence such as "log in as admin" once and reuse it in many cases, and to run one case with several rows of data, so that I keep fewer copies of the same steps and cover more inputs.

Design record: [competitive features proposal F2](../discussions/competitive-features-proposal.md#f2-shared-steps-and-data-driven-cases-m-wbs-92). Server: [server/app/modules/shared_steps](../../server/app/modules/shared_steps) (the library), [case_content_check.py](../../server/app/modules/test_cases/utils/case_content_check.py) and [case_content_rules.py](../../server/app/modules/test_cases/utils/case_content_rules.py) (case rules), [shared_step_expansion.py](../../server/app/modules/test_cases/utils/shared_step_expansion.py) (expansion). How runs use them: [RUN-14](runs.md#run-14-shared-steps-and-iterations-in-a-run-wbs-92).

- AC1 (library): a shared step belongs to one project and has a `key` (letters, digits and `_`, starting with a letter, at most 64; stored in lowercase, so `Log_In` is `log_in`), a `title` (1 to 200 characters) and versioned steps. Tables `shared_steps` (project, key, title, current version, `archived_at`) and `shared_step_versions` (number, `steps` JSONB, `data_keys`, `created_by`).
- AC2 (create): `POST /api/projects/{project_key}/shared-steps` with `{key, title, steps: [{action, expected?}]}` (1 to 50 steps; action 1 to 5000 characters) creates version 1 (201). A key already used in the project, archived steps included, gets `SHARED_STEP_KEY_ALREADY_USED` (409); so does the second of two creates of the same key sent at once (the repository maps the unique key `shared_steps_project_id_key_key` to it). A bad key gets `INVALID_REQUEST`. A step with `sharedStepKey` (a shared step inside a shared step) or without an action gets `INVALID_STEP_SHAPE` (422).
- AC3 (read): `GET …/shared-steps` lists the project's shared steps by key; archived ones only with `?archived=true`. `GET …/shared-steps/{key}` returns one (the key is matched without case). Both return `id`, `key`, `title`, `isArchived`, `archivedAt`, `currentVersion` (`id`, `number`, `steps: [{order, action, expected}]`, `dataKeys`, `createdBy`, `createdAt`), `usageCount`, `createdBy`, `createdAt`. A key of another project gets `NOT_FOUND`.
- AC4 (save): `PATCH …/shared-steps/{key}` takes `baseVersionNumber` and any of `title`, `steps`, `archived`. New steps (different actions or expected results) add a version; a title change or archiving saves without a version; a save with no change adds nothing and publishes nothing. A stale `baseVersionNumber` gets `CONFLICT`. New steps that would give a case using the shared step (its current version, Deprecated cases left out) more than 200 steps once its shared steps are expanded get `INVALID_STEP_SHAPE` (422) and add no version: "With these steps, these cases would have more than 200 steps once their shared steps are expanded: TC-n, …." `dataKeys` lists the `{{data.key}}` references in the version's steps.
- AC5 (used by): `usageCount` ("Used by N cases") counts the cases whose current version names the shared step, Deprecated cases left out. `GET …/shared-steps/{key}/usage` lists them by code: `testCaseId`, `code`, `title`, `status`, `storyJiraKey`, `versionNumber`.
- AC6 (case steps): a case step is either `{action, expected?}` or `{sharedStepKey}`. A step with both, or with neither, gets `INVALID_STEP_SHAPE` (with neither: "Step n: write the action, or pick a shared step."; with both: "Step n: a shared step has no action or expected result of its own."). A case's step list shows a shared step as `{order, action: null, expected: null, sharedStepKey}`; every plain step has `sharedStepKey: null`. The case version stores the reference, not a copy, so editing the shared step changes what the case runs next time. With its shared steps expanded, a case has at most 200 steps (the most `record_case_result` and the manual record route take); a save over that gets `INVALID_STEP_SHAPE`: "With its shared steps expanded, this case has n steps. A case can have at most 200 steps once its shared steps are expanded."
- AC7 (unknown and archived): a `sharedStepKey` that names no shared step of the project gets `UNKNOWN_SHARED_STEP` (422) and nothing is saved. An archived shared step cannot be added to a case, but a case that already used it keeps it and can still be edited; it still expands from the archived step's last version.
- AC8 (parameters and data rows): a case version has `parameters` (names: a letter, then letters, digits and `_`, at most 50 characters; at most 20, each name once without regard to case) and `dataRows` (at most 20 rows; each row is an object with exactly one value per parameter, values up to 1000 characters). Steps, preconditions and shared steps use a parameter as `{{param.name}}`; a value may be a `{{data.key}}` reference. Too many parameters or rows, a row whose names differ from the parameters, rows without parameters ("Add the parameters before the data rows."), parameters without rows ("Add at least one data row for the parameters, or remove the parameters."), or the same name twice get `INVALID_STEP_SHAPE`, so a saved case never has parameters with no row to run. Editing the parameters or rows adds a case version, like any other field.
- AC9 (no secrets in rows): a row value that contains the value of any secret of the project (any environment) gets `SECRET_IN_DATA_ROW` (422, names the row, never the value). `{{data.admin_password}}` pointing at a secret key is fine. The check runs when the rows change.
- AC10 (references and Ready): the version's `dataKeys` cover the case's own references, its data rows and the `dataKeys` of the shared steps it names (as they were when the case version was saved). `unknownReferences` and the Ready check also list `param.<name>` for a `{{param.name}}` with no such parameter. Moving to Ready (or saving a Ready case) is refused with `UNKNOWN_REFERENCE` for an unknown data key, file key or parameter, and with `INVALID_STEP_SHAPE` when the case has parameters but no data row (only a version saved before saving refused that, AC8, can still have it).
- AC11 (import and drafts): the CSV and xlsx import (CASE-9) and `create_draft_cases` (CASE-10, CASE-11) create plain steps only; shared steps, parameters and data rows are added in the editor.
- AC12 (live events): creating, saving or archiving a shared step publishes `shared_step.changed` (`ids.sharedStepKey`, `ids.sharedStepId`). Saving a case with shared steps or data rows publishes `test_case.changed` as before.
- AC13 (library screen): `/projects/[projectKey]/shared-steps` lists the shared steps in a table: title (links to the shared step), key, step count, "Used by N cases" (`usageCount`) and the current version with its date. "Show archived" adds the archived ones with an Archived badge (`?archived=true`). "New shared step" (with `test_case.edit`, project not archived) opens a dialog with title, key (lowercased and checked against the key pattern before sending; "Letters, digits and _, starting with a letter. The key can't change later.") and a step editor (1 to 50 steps, `{{data.key}}` suggestions); a key already used shows on the key field; a created step opens its page. States: "No shared steps yet" (with or without the create action), a skeleton, and "The shared steps could not be loaded." with Try again. Client: [client/src/modules/shared-steps](../../client/src/modules/shared-steps).
- AC14 (shared step page): `/projects/[projectKey]/shared-steps/[key]` shows the title, key, version and date, the steps (read-only), the test data keys it uses, and a "Used by N cases" card that lists the cases from `GET …/usage` (code links to the case, title, story, status). With `test_case.edit`: Edit (title and steps in a dialog; only the changed fields are sent with `baseVersionNumber`, so a title change adds no version) and Archive or Restore (`PATCH` with `archived`). An archived step shows "This shared step is archived. Cases that already use it keep running it, but it can't be inserted into other cases." and has no Edit. A key that can't exist, or a 404, shows "Shared step not found".
- AC15 (insert a shared step): in the case editor (new case and edit), "Insert shared step" next to "Add step" opens a dialog with a searchable list of the project's non-archived shared steps ("title (key)") and a read-only preview of the chosen one's steps; Insert adds a `{sharedStepKey}` step at the end. In the step list, and in the case's read view, a shared step is shown collapsed: a Shared step badge, its title (links to its page), its key, Archived when archived, and its step count. "Show steps" expands its current steps read-only (no fields), with each `{{data.key}}` shown as a value chip: in the read view from the chosen environment, in the editor from the project's default environment (secrets masked, no Reveal); "Hide steps" folds them again. Such a step can be moved and removed like any other; it has no action of its own to fill in. Both read `GET …/shared-steps?archived=true` once, so an archived step that a case already uses still shows; a key the list doesn't have shows "This shared step no longer exists in the project."
- AC16 (parameters and data rows editor): the case editor has a "Parameters and data rows" section under the steps: a table whose header has one name field per parameter and whose rows have one value field per parameter, with "Add parameter", "Add data row" (only once a parameter exists) and a remove button per parameter and per row (removing the last parameter removes the rows). The hint says to use `{{param.name}}` in the preconditions and steps, that each row runs the case once as one iteration, and that a value may be a `{{data.key}}` reference but never a secret. Before sending, the editor checks each name (required, a letter then letters, digits and `_`, at most 50, no name twice without regard to case), values (at most 1000 characters), the 20-parameter and 20-row limits, and that parameters have at least one data row ("Add at least one data row for the parameters, or remove the parameters.", the server rule of AC8). A new case sends `parameters` and `dataRows` only when it has parameters; a save sends both together when either changed. The read view shows a "Data rows (n iterations)" table (one column per parameter, one row per iteration).

## Rules

Status transitions (`TEST_CASE_STATUS_TRANSITIONS` in [test_case_status.py](../../server/app/modules/test_cases/typing/constants/test_case_status.py)); the diagram is in [user-flows.md](../design/user-flows.md#test-case-status).

| From | To |
| --- | --- |
| `draft` | `in_review`, `deprecated` |
| `in_review` | `draft`, `ready`, `deprecated` |
| `ready` | `in_review`, `draft`, `deprecated` |
| `deprecated` | `draft` |

| Limit | Value | Code |
| --- | --- | --- |
| Title | 200 characters | `MAX_TITLE_LENGTH` |
| Business value, preconditions, step action, expected result | 5000 characters each | `MAX_TEXT_LENGTH` |
| Steps per case | 100 | `MAX_STEPS` |
| Steps per case with its shared steps expanded | 200 (the most a result reports, `MAX_STEPS_PER_CASE`) | `MAX_EXPANDED_CASE_STEPS` |
| AC links per case | 50 | `MAX_CRITERION_LINKS` |
| Data and file key | `^[A-Za-z][A-Za-z0-9_.-]{0,99}$` | `FILE_KEY_PATTERN` |
| Case code | `TC-<n>`, n from 1 | `CASE_CODE_PATTERN` |
| Import file | 5 MB, 500 cases, 5000 rows | `MAX_CASE_IMPORT_BYTES`, `MAX_IMPORTED_CASES`, `MAX_IMPORT_ROWS` |
| Cases per `check_draft_cases` or `create_draft_cases` call | 1 to 100 | `MAX_DRAFT_CASES_PER_CALL` |
| Draft case `source` | 200 characters | `MAX_DRAFT_CASE_SOURCE_LENGTH` |
| Test file | 20 MB, project allowed types | `MAX_FILE_BYTES` |
| Review comment | 5000 characters | `MAX_REVIEW_COMMENT_LENGTH` |
| Label name | 1 to 40 characters, unique per project without case | `MAX_LABEL_NAME_LENGTH` |
| Labels per case, label filters per list request | 20 | `MAX_LABELS_PER_CASE` |
| Flaky window and threshold | last 10 decisive results on the current version, 3 flips | `FLAKY_RESULT_WINDOW`, `FLAKY_FLIP_THRESHOLD` |
| Disagreement window | 24 hours between the latest manual and automated result | `DISAGREEMENT_WINDOW` |
| Auto-release from quarantine | 10 passes in a row after quarantine | `QUARANTINE_RELEASE_PASS_COUNT` |
| Quarantine reason | 500 characters | `MAX_QUARANTINE_REASON_LENGTH` |
| Nightly flaky sweep | `45 3 * * *` (UTC) | `test_cases.sweep_flaky` |
| Shared step key | `^[a-z][a-z0-9_]{0,63}$` after trimming and lowercasing | `SHARED_STEP_KEY_PATTERN` |
| Shared step title; steps per shared step | 200 characters; 1 to 50 | `MAX_SHARED_STEP_TITLE_LENGTH`, `MAX_SHARED_STEP_ACTIONS` |
| Parameters and data rows per case | 20 each | `MAX_PARAMETERS`, `MAX_DATA_ROWS` |
| Parameter name; data row value | `^[A-Za-z][A-Za-z0-9_]{0,49}$`; 1000 characters | `PARAMETER_NAME_PATTERN`, `MAX_DATA_VALUE_LENGTH` |

- Priorities: `critical`, `high`, `medium`, `low`.
- Test files cannot be deleted; upload a new version instead.
- The case list has no paging.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/test-cases` | "No test cases yet" | table skeleton | "The test cases could not be loaded." + Try again | New and Import hidden | New and Import hidden | `test_case.changed`, `label.changed`; latest results also on `run.case_recorded`, `run.finished` |
| `/projects/[projectKey]/test-cases/new` | – | – | field errors | "You can't create test cases" | "You can't create test cases" | – |
| `/projects/[projectKey]/test-cases/[caseCode]` | Files: "No files yet…"; History: "Only one version so far."; Review: "No open comments"; Compare: "Only one version so far. Compare two versions after the next save." | skeleton | "The test case could not be loaded."; "Test case not found"; Review: "The review comments could not be loaded." + Try again; Compare: "The versions could not be loaded." + Try again | read-only (Quarantine and Edit labels hidden) | read-only; Quarantine and Release hidden without `test_case.quarantine`; Edit labels hidden without `test_case.edit` | `test_case.changed` (also quarantine history), `review_comment.changed`, `label.changed` |
| `/projects/[projectKey]/shared-steps` | "No shared steps yet" | table skeleton | "The shared steps could not be loaded." + Try again | New hidden | New hidden without `test_case.edit` | `shared_step.changed`, `test_case.changed` |
| `/projects/[projectKey]/shared-steps/[key]` | Used by: "No case uses this shared step yet" | skeleton | "The shared step could not be loaded." + Try again; "Shared step not found"; Used by: "The cases that use this shared step could not be loaded." + Try again | Edit and Archive hidden | Edit and Archive hidden without `test_case.edit` | `shared_step.changed`, `test_case.changed` |
| Import dialog | "No test cases were found in this file." | "Reading the file" | error per code (see Errors) | hidden | hidden | – |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/test-cases` | `test_case.view` |
| `POST /api/projects/{project_key}/test-cases` | `test_case.edit` |
| `GET /api/projects/{project_key}/test-cases/{case_code}` | `test_case.view` |
| `PATCH /api/projects/{project_key}/test-cases/{case_code}` | `test_case.edit` |
| `GET /api/projects/{project_key}/test-cases/{case_code}/versions` | `test_case.view` |
| `PUT /api/projects/{project_key}/test-cases/{case_code}/status` | `test_case.edit` |
| `POST /api/projects/{project_key}/test-cases/{case_code}/review` | `test_case.edit` |
| `GET /api/projects/{project_key}/test-cases/{case_code}/review-comments` | `test_case.view` |
| `POST /api/projects/{project_key}/test-cases/{case_code}/review-comments` | `test_case.edit` |
| `PUT /api/projects/{project_key}/test-cases/{case_code}/review-comments/{comment_id}/resolve` | `test_case.edit` |
| `PUT /api/projects/{project_key}/test-cases/{case_code}/labels` | `test_case.edit` |
| `PUT /api/projects/{project_key}/test-cases/{case_code}/quarantine` | `test_case.quarantine` |
| `DELETE /api/projects/{project_key}/test-cases/{case_code}/quarantine` | `test_case.quarantine` |
| `GET /api/projects/{project_key}/test-cases/{case_code}/quarantine-events` | `test_case.view` |
| `GET /api/projects/{project_key}/labels` | `test_case.view` |
| `POST /api/projects/{project_key}/labels` | `test_case.edit` |
| `PATCH /api/projects/{project_key}/labels/{label_id}` | `test_case.edit` |
| `DELETE /api/projects/{project_key}/labels/{label_id}` | `test_case.edit` |
| `GET /api/projects/{project_key}/shared-steps?archived=` | `test_case.view` |
| `POST /api/projects/{project_key}/shared-steps` | `test_case.edit` |
| `GET /api/projects/{project_key}/shared-steps/{key}` | `test_case.view` |
| `PATCH /api/projects/{project_key}/shared-steps/{key}` | `test_case.edit` |
| `GET /api/projects/{project_key}/shared-steps/{key}/usage` | `test_case.view` |
| `POST /api/projects/{project_key}/test-cases/{case_code}/files` | `test_case.edit` |
| `GET /api/projects/{project_key}/test-cases/{case_code}/files/{file_key}/versions` | `test_case.view` |
| `POST /api/projects/{project_key}/test-case-imports/preview` | `test_case.edit` |
| `POST /api/projects/{project_key}/test-case-imports/commit` | `test_case.edit` |
| `POST /api/projects/{project_key}/uploads`, `POST …/uploads/{file_id}/complete` | `test_case.edit` (kind `test_file`), `test_data.edit` (kind `import`) |
| `GET /api/projects/{project_key}/files/{file_id}` | `file.download` |
| `GET /api/projects/{project_key}/case-latest-results?storyKey=` | `report.view` |

| MCP `check_draft_cases(cases[])` | `test_case.edit` |
| MCP `create_draft_cases(cases[])` | `test_case.edit` |

Claude reads Ready cases through the MCP tool `get_story_context` ([runs.md](runs.md)). The two draft-case tools work in the token's project.

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown case code, story, test file, import file, case version, review comment, label or shared step (one of another project counts as unknown) |
| `CONFLICT` | Stale `baseVersionNumber` (case or shared step); editing or commenting on a deprecated case; a file already attached elsewhere; a label name already used in the project |
| `INVALID_STATUS_TRANSITION` | A status move not in the table |
| `CASE_NOT_READY` | Ready with no steps |
| `UNKNOWN_REFERENCE` | Ready (or saving a Ready case) with an unknown `{{data.…}}`, `{{file.…}}` or `{{param.…}}` |
| `SHARED_STEP_KEY_ALREADY_USED` | Creating a shared step with a key the project already has, also when two creates of one key race (409) |
| `UNKNOWN_SHARED_STEP` | A case step names a shared step the project does not have, or adds an archived one (422) |
| `INVALID_STEP_SHAPE` | A step that is neither `{action, expected}` nor `{sharedStepKey}`; a shared step inside a shared step; more than 20 parameters or data rows; a row that does not match the parameters; rows without parameters or parameters without rows; a case over 200 steps with its shared steps expanded, or a shared step save that would make a case so long; Ready with parameters but no data row (422) |
| `SECRET_IN_DATA_ROW` | A data row holds a literal secret value (422) |
| `REVIEW_COMMENTS_OPEN` | Ready while a review comment of the case is open (409) |
| `REVIEWER_IS_AUTHOR` | Ready or Mark reviewed by the author of the current version while the project requires a separate reviewer (403) |
| `INVALID_REQUEST` | AC not linkable, wrong file kind, import choice not importable, `create_draft_cases` with a case that has a problem, a review comment on a step the version does not have, a case label that is not a label of the project, validation |
| `UPLOAD_NOT_COMPLETED` | Attaching or importing a file whose upload did not finish |
| `FILE_TYPE_NOT_ALLOWED`, `FILE_TOO_LARGE` | Upload outside the project's types or over the size limit |
| `IMPORT_INVALID_FILE` | The spreadsheet cannot be read |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | No `test_case.edit` (or `test_case.quarantine` for quarantine), or the project is archived (both draft-case tools included) |
| `INVALID_API_TOKEN` | A draft-case tool called with a bad, expired or revoked token |

## Later

Nothing planned.

## Differences from the proposals

- The [server proposal §7](../discussions/server-proposal.md#7-rest-api) addressed cases by id; the code uses the case code (`/test-cases/TC-12`).
- The [workflow proposal §5](../discussions/testing-workflow-proposal.md#5-roles-and-permissions) gave BA and Dev "view + comment" on test cases. Review comments (CASE-15) need `test_case.edit`, as the [build plan §4.2](../discussions/competitive-features-plan.md#42-new-capabilities) says, so BA, Dev, PM and Viewer only read them.
- Import reads an uploaded `.xlsx` or `.csv`, not a Google Sheet link (no Google sign-in).
- Files belong to the case under a key, not to a single step.

## Open points

- Blocker for 3.6.7: no sample of the team's sheet has arrived, so the column names above are a guess (assumption 3.6.7).
- A case created or edited through the API with a NUL character in business value or preconditions gets a 500 from Postgres; the import strips them (W4 carry-over).
- Not checked in a browser: the editor at 375 px, a real signed upload to RustFS, and a real xlsx import.
- Not checked in a browser: the Review and Compare tabs (CASE-15 AC8 to AC12) and the Review settings card (SET-4 AC5). They have Vitest and axe tests only. The Compare table scrolls sideways on a phone, like other tables.
- CASE-10 and CASE-11 are not checked in a real Claude Code session or on a real QC file. The tools have API tests; the skills have only file checks (B-7, B-9).
- CASE-16: a `{{param.name}}` inside a shared step is not checked against the parameters of each case that uses it, and the shared step's data keys in a case version are those of the shared step when the case was saved (a later shared step edit updates them only at the next case save; runs and the context tools always read the current ones). Assumption W10.T5.
- CASE-15: editing a Ready case keeps it Ready (CASE-6 AC4), so with "Reviewer must not be the author" on, an author can still change a Ready case without a second review. Moving it back to In review is left to the team (assumption W9.T5).
