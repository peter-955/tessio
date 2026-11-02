# Environments and test data

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.9 · Story prefix DATA · Index: [README](README.md)

## Purpose

Environments say where tests run (base URL and health-check URL). Test data replaces the shared data file: plain values and secrets, each key with an optional description, kept for the whole project or per environment, and referenced from steps as `{{data.key}}`. Secrets are encrypted, never listed, shown only to Admin and QC on demand, given to Claude only for its own running run, and masked in every result and report. Server: [server/app/modules/test_data](../../server/app/modules/test_data), `set_test_data` in the same module, `resolve_data` in [server/app/modules/story_context](../../server/app/modules/story_context), audit in [server/app/modules/audit](../../server/app/modules/audit). Client: [client/src/modules/test-data](../../client/src/modules/test-data) and [client/src/modules/environments](../../client/src/modules/environments).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List environments | `project.view` | all |
| Create, edit, archive, unarchive, delete environments | `environment.manage` | Admin, QC, Dev |
| List test data and the effective values | `test_data.view` | all (secret values hidden) |
| Create, edit, delete, import variables and endpoints; MCP `set_test_data` | `test_data.edit` | Admin, QC, Dev |
| The same for secrets | `test_data.edit` + `secret.edit` | Admin, QC |
| Reveal a secret in the UI | `secret.reveal` | Admin, QC (also on archived projects) |
| Get secret values for one's own running run (MCP `resolve_data`) | `secret.use_in_run` | Admin, QC, Dev |

## User stories

### DATA-1 Environment list (WBS 3.9.1)

As a QC, I want the project's environments with their URLs, so that runs target the right place.

- AC1: The Environments tab of `/projects/[projectKey]/test-data` lists name, base URL, health-check URL, status (Active, Archived) and the project default, from `GET /api/projects/{project_key}/environments`.
- AC2: "Show archived" adds archived environments.
- AC3: With none: "No environments yet. Add the places where tests run, such as staging or production."

### DATA-2 Create and edit an environment (WBS 3.9.2)

As a QC or Dev, I want to add and change environments, so that the list matches our servers.

- AC1: "Add environment" posts name (1 to 100 characters), base URL and optional health-check URL (each `http://` or `https://`, no spaces, up to 2000 characters) to `POST /api/projects/{project_key}/environments`. "Edit" uses `PUT …/environments/{environment_id}`.
- AC2: Names are unique per project without case (`ENVIRONMENT_NAME_ALREADY_USED`).
- AC3: "Archive" (`POST …/archive`) hides an environment from new runs and clears it as the project default; "Unarchive" brings it back.
- AC4: "Delete" (`DELETE …/environments/{environment_id}`) removes an environment and its own test data, but only when no run used it; otherwise `ENVIRONMENT_IN_USE` ("Runs use this environment. Archive it instead.").
- AC5: The project default environment is set in [project settings](settings.md).

### DATA-3 Test data per project and per environment (WBS 3.9.3)

As a QC, I want variables, endpoints and secrets for the project and per environment, so that one step works on Dev and Staging.

- AC1: The Data tab shows a grid: one row per key, an "All environments" column for project values and one column per environment.
- AC2: "Add data" posts key, value (1 to 10 000 characters), scope (`environmentId`, or none for All environments), the "Secret" checkbox as `kind` (`secret`, otherwise `variable`) and an optional description to `POST /api/projects/{project_key}/test-data`. "Edit" uses `PUT …/test-data/{item_id}`; "Delete" uses `DELETE …/test-data/{item_id}`.
- AC3: A key starts with a letter and uses letters, digits, `_`, `.` and `-` (at most 100 characters). A key is unique per scope (`TEST_DATA_KEY_ALREADY_USED`).
- AC4: An environment value overrides the project value with the same key. A cell without its own value shows "Uses All environments value". `GET …/test-data/effective?environmentId=` returns the merged list.
- AC5: Writing into an archived environment gets `INVALID_REQUEST` ("This environment is archived.").
- AC6: Dev can edit plain values but not secrets; the Secret checkbox is disabled with "Only Admins and QC can save secrets.".
- AC7: A key has **one description** (up to 500 characters), shared by its All environments value and every environment value (table `test_data_descriptions`). Leaving `description` out of a save keeps it, an empty or blank one clears it, a renamed key takes it along, and deleting the key's last value deletes it. List and effective-data responses return it.
- AC8: The grid shows the description under the key, and any value starting with `http://` or `https://` is a link. The `{{data` suggestions in the case editor show the description next to the key, and `get_story_context` gives it to Claude with each data key.

### DATA-4 Secret masking and reveal (WBS 3.9.4)

As an Admin or QC, I want secrets hidden by default and revealed only on demand, so that passwords are not on everyone's screen.

- AC1: Secret values are stored encrypted with AES-256-GCM and are never returned by list calls.
- AC2: "Reveal" calls `POST /api/projects/{project_key}/test-data/{item_id}/reveal` and shows the value; it hides again after 30 seconds. Revealing a non-secret gets `INVALID_REQUEST`.
- AC3: Each reveal writes a `secret.reveal` audit event with the user, project, item and API token (if any).
- AC4: Other roles see "Only Admins and QC can see secret values".
- AC5: Editing a secret with an empty value keeps the current value ("Leave empty to keep the current value").

### DATA-5 Secrets during a run (WBS 3.9.4)

As Claude running a case, I want the secret values the case needs, so that I can sign in without anyone pasting passwords.

- AC1: `get_story_context` returns secrets only as `{{data.key}}`, never the value.
- AC2: `resolve_data(run_id, keys[])` (1 to 50 keys, each up to 100 characters) returns values only for the caller's own `running` run (`RUN_NOT_OWNED`, `RUN_NOT_RUNNING`), only for keys the run's cases use, and only secrets, using the run's environment (environment value over project value). Other keys come back in `unknown_keys`.
- AC3: Each resolved key writes a `secret.resolve` audit event with the user, project, item, API token and run.
- AC4: Every step result, case error, run summary and report is masked: any value of the environment's secrets (project and environment scope) is replaced by `••••`. This also applies to manual runs.

### DATA-6 Import the shared data file (WBS 3.9.5)

As a QC, I want to import our existing data file, so that I don't retype every value.

- AC1: "Import" takes a `.env`, `.json`, `.yaml` or `.yml` file up to 1 MB (upload kind `import`) and a scope ("Import into"). Only the person who uploaded the file can preview or commit it.
- AC2: `POST /api/projects/{project_key}/test-data/import/preview` lists each key with its value, a suggested kind and the change (New, Update, Unchanged). Nested JSON and YAML keys are joined with `.`.
- AC3: Keys that look secret (password, pwd, secret, token, api key, private key, credential) are suggested as `secret`; the rest as `variable`. In a `.env` file, the comment lines right above a key become its description (joined, up to 500 characters); a blank line in between drops them. The preview shows the description, and the commit saves it.
- AC4: Skipped lines are listed: not a key and value, invalid key, unsupported value (only text, numbers and true or false), value longer than 10 000 characters.
- AC5: `POST …/test-data/import/commit` writes the chosen keys (up to 1000) with their kinds. A user without `secret.edit` cannot import secret rows ("Rows that look like secrets are left out…").

### DATA-7 Save missing test data from Claude (WBS 9.18)

As the person answering a missing-test-data gap with `/tessio:answer-gaps`, I want Claude to save the value I confirmed, so that the next run finds it.

- AC1: MCP `set_test_data(key, value, kind, environment?)` (`test_data.edit`: Admin, QC, Dev) writes one plain value in the token's project. The key follows the key rule (DATA-3 AC3), the value is 1 to 10 000 characters.
- AC2: `kind` is `variable` or `endpoint`; both are stored as `variable` (endpoints were merged into variables). `kind="secret"` is refused with `INVALID_REQUEST` ("Claude never saves secrets. Add the secret on the Test data page.") and nothing is saved.
- AC3: Without `environment` the value goes to All environments. With `environment` (an environment name, matched without case) it goes to that environment, where it overrides the project value; the project value is not changed. An unknown environment gets `NOT_FOUND`, an archived one `INVALID_REQUEST` ("This environment is archived.").
- AC4: When the key already has a value in that scope it is updated; otherwise a new value is created. The key's description is kept. The reply is `{"action": "created" | "updated" | "unchanged"}`; a project write also lists in `overridden_in` the active environments whose own value still wins.
- AC5: When any value of the key is a secret (in any scope), the write is refused with `INVALID_REQUEST` ("This key is a secret. Change it on the Test data page."), so Claude never puts a plain value next to a secret.
- AC6: Viewers get `PERMISSION_DENIED`; an archived project gets `PROJECT_ARCHIVED`. Nothing is audited (only secrets are), and no live event is sent: the Data tab refetches as before.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Data kinds | `variable`, `secret` (`endpoint` was merged into `variable` by migration 0015) | `DataItemKind` |
| Key description | 500 characters, one per key | `MAX_DATA_ITEM_DESCRIPTION_LENGTH` |
| Key | `^[A-Za-z][A-Za-z0-9_.-]{0,99}$` | `DATA_ITEM_KEY_PATTERN` |
| Value | 10 000 characters | `MAX_DATA_ITEM_VALUE_LENGTH` |
| Import file | 1 MB, 1000 items | `MAX_IMPORT_BYTES`, `MAX_IMPORT_ITEMS` |
| Import formats | `dotenv`, `json`, `yaml` | `ImportFormat` |
| Environment name | 100 characters, unique without case | `MAX_ENVIRONMENT_NAME_LENGTH` |
| Environment URL | `^https?://\S+$`, 2000 characters | `ENVIRONMENT_URL_PATTERN` |
| `resolve_data` keys per call | 50 | `MAX_RESOLVE_KEYS` |
| Masked value | `••••` | `MASKED_VALUE` |
| Reveal auto-hide (client) | 30 s | `SECRET_REVEAL_DURATION_IN_MILLISECONDS` |
| Audit actions | `secret.reveal`, `secret.resolve` | `AuditAction` |

- Effective data for an environment: the environment's own items plus the project items whose key it does not override.
- The run picks its environment as described in [RUN-2](runs.md#run-2-start-a-claude-run-wbs-3103).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/test-data` (Data tab) | "No test data yet. Add variables, endpoints and secrets, or import a .env, JSON or YAML file."; no environments: values in All environments apply everywhere | "Loading test data" | "Test data could not be loaded."; environments failing: only the All environments column | read-only; Reveal still works for Admin and QC | Add, Import, Edit hidden; secret cells show "Hidden secret value" | – (refetch after each action) |
| Environments tab | "No environments yet" | "Loading environments" | "Environments could not be loaded." | read-only | actions hidden without `environment.manage` | – |

## API

| Method and path or MCP tool | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/environments` | `project.view` |
| `POST /api/projects/{project_key}/environments` | `environment.manage` |
| `PUT /api/projects/{project_key}/environments/{environment_id}` | `environment.manage` |
| `POST /api/projects/{project_key}/environments/{environment_id}/archive` | `environment.manage` |
| `POST /api/projects/{project_key}/environments/{environment_id}/unarchive` | `environment.manage` |
| `DELETE /api/projects/{project_key}/environments/{environment_id}` | `environment.manage` |
| `GET /api/projects/{project_key}/test-data` | `test_data.view` |
| `GET /api/projects/{project_key}/test-data/effective?environmentId=` | `test_data.view` |
| `POST /api/projects/{project_key}/test-data` | `test_data.edit` (+ `secret.edit` for secrets) |
| `PUT /api/projects/{project_key}/test-data/{item_id}` | `test_data.edit` (+ `secret.edit` for secrets) |
| `DELETE /api/projects/{project_key}/test-data/{item_id}` | `test_data.edit` (+ `secret.edit` for secrets) |
| `POST /api/projects/{project_key}/test-data/{item_id}/reveal` | `secret.reveal` |
| `POST /api/projects/{project_key}/test-data/import/preview` | `test_data.edit` |
| `POST /api/projects/{project_key}/test-data/import/commit` | `test_data.edit` (+ `secret.edit` for secret rows) |
| MCP `resolve_data(run_id, keys[])` | `secret.use_in_run` |
| MCP `set_test_data(key, value, kind, environment?)` | `test_data.edit` (plain values only) |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown environment, data item or import file |
| `ENVIRONMENT_NAME_ALREADY_USED` | Same environment name in the project |
| `ENVIRONMENT_IN_USE` | Deleting an environment a run used |
| `TEST_DATA_KEY_ALREADY_USED` | Same key in the same scope |
| `INVALID_REQUEST` | Archived environment as scope, reveal of a non-secret, missing value, a commit key not in the file, `set_test_data` with `kind="secret"` or on a key that holds a secret |
| `UPLOAD_NOT_COMPLETED` | Import before the upload finished |
| `FILE_TOO_LARGE` | Import file over 1 MB |
| `IMPORT_INVALID_FILE` | The file is not valid `.env`, JSON or YAML |
| `RUN_NOT_OWNED`, `RUN_NOT_RUNNING` | `resolve_data` for someone else's run or a finished run |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or a write on an archived project |

## Later

- 3.9.6 "Where used" list for each data key.
- Re-encrypting stored secrets under a new key (the key ring can read old keys, see [NFR-SEC](non-functional-requirements.md#sec-security)).

## Differences from the proposals

- The [workflow proposal §5](../discussions/testing-workflow-proposal.md#5-roles-and-permissions) let only Dev use secrets in runs. In code QC and Admin can call `resolve_data` too, and a workspace admin acts as Admin in the UI (reveal included).
- Environments can be deleted when unused; the proposals only had archive.
- Masking covers all of the environment's secret values, not only the keys a case used (assumption 4.7).

## Open points

- Blocker for 3.9.5: no sample of the team's shared data file has arrived; `.env`, JSON and YAML are assumed (assumption 3.9.5).
- A secret encrypted with a key that is no longer in the key ring fails with a 500 on reveal, import and `resolve_data`.
- Two environments whose names differ only in case can both be created if the requests race (no database guard).
- Not checked in a browser: a real import upload (needs bucket CORS) and the 375 px grid.
