# Why it failed: diagnosis and suspected cause

**Status:** Accepted, built on 2026-11-01 (what the code does is in the [runs spec, RUN-4 AC5b, RUN-7 AC9 and RUN-8 AC10](../spec/runs.md#run-4-record-a-case-result-wbs-3102-3103) and the [failures spec, FAIL-1 AC7 and FAIL-6](../spec/failures.md#fail-6-suspected-cause-wbs-3116))
**Date:** 2026-11-01
**WBS:** [3.10.11](../wbs/wbs.md#310-runs), [3.11.6](../wbs/wbs.md#311-failures), [4.14](../wbs/wbs.md#4-server-python--fastapi-adr-0004-details-in-the-server-proposal), [5.14](../wbs/wbs.md#5-claude-integration)
**Related:** [execution log proposal](execution-log-proposal.md) (how Claude got there; this one is why the step failed)

## Decisions at a glance

| Area | Decision (Peter, 2026-11-01) |
| --- | --- |
| Goal | When a case fails, the team sees the likely reason, not only what the screen showed. |
| What Claude captures | On the failed or blocked step only: page URL, up to 5 console errors, up to 5 failed requests (method, path, status, first 500 characters of the error body). |
| Suspected cause | One per failed or blocked case: App bug, Test data, Environment, Test case out of date or Unknown, with a one-sentence reason. Claude sets it; a tester sets it in a manual run. |
| Correcting it | Admin, QC or Dev can change it on the failure (`failure.assign`). The change is recorded in the timeline, and later failed results no longer overwrite it. |
| Where it shows | The run detail (under the case and on the failing step), the report's failed cases, the failure detail and the recorded manual case. |
| Secrets | Query strings and fragments are dropped; every text is masked against the environment's secrets, as actual results are. |

## 1. Why

A failed step kept only free-text actual result and error, plus a screenshot. The reason often lives outside the screenshot: a `502` from an API, a JavaScript exception, an expired test card. Claude in Chrome can read the console and network, but the skill never asked it to. Nothing told a Dev whether a failure was a product bug or a test problem.

## 2. How it works

1. The `run-story-tests` skill (step 6 of `execute-cases.md`) reads `read_console_messages` and `read_network_requests` at the failing step, keeps the errors and the 4xx/5xx requests, and picks a suspected cause from fixed rules.
2. `record_case_result` takes the new step fields (`page_url`, `console_errors`, `failed_requests`) and case fields (`suspected_cause`, `cause_reason`). The manual record route takes `suspectedCause` and `causeReason`.
3. The server stores the diagnosis as JSON on the step result and the cause on the case result, then copies the cause to the failure.
4. `PUT /api/projects/{project_key}/failures/{failure_id}/cause` changes it and adds a `cause_changed` event.

## 3. Not in this proposal

- Diagnosis on passed steps.
- Full request and response bodies, or HAR files.
- Statistics of causes across runs.

## 4. Open points

- Not tried yet on a real Claude in Chrome run. The cause rules may need tuning after the pilot.
