# Test data: key, value, description, and a Secret checkbox

**Status:** Accepted
**Date:** 2026-11-01
**WBS:** [3.9.7](../wbs/wbs.md#39-environments--test-data)
**Related:** [environments and test data spec](../spec/environments-and-test-data.md)

## Decisions at a glance

| Area | Decision (Peter, 2026-11-01) |
| --- | --- |
| Form | Key, value, **description** and a **Secret** checkbox. Scope (All environments or one environment) stays. |
| Kinds | `endpoint` is removed. Existing endpoints become plain values. `variable` and `secret` stay in the API; the UI shows them as the checkbox. |
| Description | **One per key**, shared by the All environments value and every environment's value. |
| Claude | Sees each key's description in `get_story_context`. |

## 1. Why

Environments with shared and per-environment values already exist (DATA-1 to DATA-6), like Postman's environments. What's missing is a way to say **what a key is for**: without that, the team can't tell which values to reuse, and neither can Claude. The variable/endpoint/secret choice also adds a decision that changes almost nothing: "endpoint" only turns a value into a link and is an import hint.

## 2. Changes

**Data**
- A new table `test_data_descriptions` (`project_id`, `key`, `description` up to 500 characters) holds **one description per key**, shared by every scope. Saving any value of a key with a description sets it for the key; an empty description clears it. Deleting a key's last value deletes its description.
- A migration turns `endpoint` into `variable` and removes it from `DataItemKind`.

**API**
- `POST` and `PUT …/test-data` take `description`. List, effective-data and run-sheet responses return it.
- `kind` takes only `variable` or `secret`. The request shape is unchanged.

**Screen**
- The form becomes key, value, description, Secret, scope. Secret is shown only to people with `secret.edit`, as today.
- The grid shows the description under the key. Any value that starts with `http://` or `https://` is a link, whatever its kind.
- The `{{data` suggestions in the case editor show the description next to each key.

**Import**
- In a `.env` file, the comment lines right above a key become its description. JSON and YAML have no comments, so they import no description.
- The suggested kind is `secret` or `variable`.

**Claude**
- `get_story_context` returns `description` with each data key the cases use. The run skills tell Claude to read it when a step's value is unclear.

## 3. Open points

- None. This is a small change on top of DATA-3 and DATA-6.
