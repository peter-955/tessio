# Test cases

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.6 · Story prefix CASE · Index: [README](README.md)

## Purpose

Test cases replace the Google Sheet. Each case belongs to one story, covers one or more of its AC, has numbered steps with expected results, may reference test data and files, and goes through a review before it can run. Every save adds a version, and every run records the version it ran. Server: [server/app/modules/test_cases](../../server/app/modules/test_cases). Client: [client/src/modules/test-cases](../../client/src/modules/test-cases).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List, open, versions, file versions, download files | `test_case.view`, `file.download` | all |
| Create, edit, change status, mark reviewed, attach files, import | `test_case.edit` | Admin, QC |
| Upload an import file | `test_data.edit` (upload kind `import`) | Admin, QC, Dev |

Without `test_case.edit` the editor is read-only ("You can view this case but not edit it."). The new-case page says "You can't create test cases".

## User stories

### CASE-1 Test case list (WBS 3.6.1)

As a QC, I want all cases of the project with filters, so that I find the ones I need.

- AC1: `/projects/[projectKey]/test-cases` lists code, title, story, priority, status, step count, AC count, last saved, a Needs review mark and the latest result.
- AC2: Filters: story (`storyKey`), status, priority, acceptance criterion (`criterionId`, needs a story first), "Needs review only" (`needsReview`), and search by code or title (`query`, up to 100 characters).
- AC3: The story detail has a Test cases tab with the same list for that story.
- AC4: With no cases: "No test cases yet. Write a case for a story, or import cases from a spreadsheet." With filters and no match: "No cases match these filters."

### CASE-2 Write a test case (WBS 3.6.2)

As a QC, I want to write a case with business value, preconditions, steps and expected results, so that anyone can run it the same way.

- AC1: "New test case" (`/projects/[projectKey]/test-cases/new`) posts to `POST /api/projects/{project_key}/test-cases` with the story key, title (1 to 200 characters), priority (`critical`, `high`, `medium` by default, `low`), business value and preconditions (each up to 5000), steps and AC links.
- AC2: A step has an action (1 to 5000 characters) and an optional expected result (up to 5000). A case has at most 100 steps; steps can be added, moved up or down, and removed.
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
- AC3: Any Admin or QC may mark a case Ready, including the author.
- AC4: Editing keeps the status. Editing a Ready case runs the Ready checks on the new version.
- AC5: A `deprecated` case cannot be edited (`CONFLICT`, "Restore the test case to Draft before editing it.") and is left out of runs and coverage. Deprecate asks "Deprecate {code}?".
- AC6: Only `ready` cases can run ([runs.md](runs.md)).

### CASE-7 Version history (WBS 3.6.6)

As a QC, I want every save kept, so that I can see what changed and which version a run used.

- AC1: `PATCH /api/projects/{project_key}/test-cases/{case_code}` sends the changes with `baseVersionNumber`. A save adds version n+1; versions are never changed. A save with no real change adds nothing.
- AC2: If someone saved meanwhile, the save gets `CONFLICT` ("Someone saved a newer version. Reload to see it.").
- AC3: The History tab lists versions (`GET …/versions`) with who saved them, and "Compare versions" shows field and step differences.
- AC4: A run fixes each case's version when it starts; the run detail shows "v{number}".

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
| AC links per case | 50 | `MAX_CRITERION_LINKS` |
| Data and file key | `^[A-Za-z][A-Za-z0-9_.-]{0,99}$` | `FILE_KEY_PATTERN` |
| Case code | `TC-<n>`, n from 1 | `CASE_CODE_PATTERN` |
| Import file | 5 MB, 500 cases, 5000 rows | `MAX_CASE_IMPORT_BYTES`, `MAX_IMPORTED_CASES`, `MAX_IMPORT_ROWS` |
| Test file | 20 MB, project allowed types | `MAX_FILE_BYTES` |

- Priorities: `critical`, `high`, `medium`, `low`.
- Test files cannot be deleted; upload a new version instead.
- The case list has no paging.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/test-cases` | "No test cases yet" | table skeleton | "The test cases could not be loaded." + Try again | New and Import hidden | New and Import hidden | `test_case.changed`; latest results also on `run.case_recorded`, `run.finished` |
| `/projects/[projectKey]/test-cases/new` | – | – | field errors | "You can't create test cases" | "You can't create test cases" | – |
| `/projects/[projectKey]/test-cases/[caseCode]` | Files: "No files yet…"; History: "Only one version so far." | skeleton | "The test case could not be loaded."; "Test case not found" | read-only | read-only | `test_case.changed` |
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
| `POST /api/projects/{project_key}/test-cases/{case_code}/files` | `test_case.edit` |
| `GET /api/projects/{project_key}/test-cases/{case_code}/files/{file_key}/versions` | `test_case.view` |
| `POST /api/projects/{project_key}/test-case-imports/preview` | `test_case.edit` |
| `POST /api/projects/{project_key}/test-case-imports/commit` | `test_case.edit` |
| `POST /api/projects/{project_key}/uploads`, `POST …/uploads/{file_id}/complete` | `test_case.edit` (kind `test_file`), `test_data.edit` (kind `import`) |
| `GET /api/projects/{project_key}/files/{file_id}` | `file.download` |
| `GET /api/projects/{project_key}/case-latest-results?storyKey=` | `report.view` |

Claude reads Ready cases through the MCP tool `get_story_context` ([runs.md](runs.md)).

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown case code, story, test file or import file |
| `CONFLICT` | Stale `baseVersionNumber`; editing a deprecated case; a file already attached elsewhere |
| `INVALID_STATUS_TRANSITION` | A status move not in the table |
| `CASE_NOT_READY` | Ready with no steps |
| `UNKNOWN_REFERENCE` | Ready (or saving a Ready case) with an unknown `{{data.…}}` or `{{file.…}}` |
| `INVALID_REQUEST` | AC not linkable, wrong file kind, import choice not importable, validation |
| `UPLOAD_NOT_COMPLETED` | Attaching or importing a file whose upload did not finish |
| `FILE_TYPE_NOT_ALLOWED`, `FILE_TOO_LARGE` | Upload outside the project's types or over the size limit |
| `IMPORT_INVALID_FILE` | The spreadsheet cannot be read |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | No `test_case.edit`, or the project is archived |

## Later

- 3.6.8 Claude drafts test cases from AC for QC to review.

## Differences from the proposals

- The [server proposal §7](../discussions/server-proposal.md#7-rest-api) addressed cases by id; the code uses the case code (`/test-cases/TC-12`).
- The [workflow proposal §5](../discussions/testing-workflow-proposal.md#5-roles-and-permissions) gave BA and Dev "view + comment" on test cases. There are no case comments; BA and Dev can only view.
- Import reads an uploaded `.xlsx` or `.csv`, not a Google Sheet link (no Google sign-in).
- Files belong to the case under a key, not to a single step.

## Open points

- Blocker for 3.6.7: no sample of the team's sheet has arrived, so the column names above are a guess (assumption 3.6.7).
- A case created or edited through the API with a NUL character in business value or preconditions gets a 500 from Postgres; the import strips them (W4 carry-over).
- Not checked in a browser: the editor at 375 px, a real signed upload to RustFS, and a real xlsx import.
