# Execute the cases of a started run

Use the reply of `start_run`: `run_id`, `base_url`, `health_check_url` and the cases with their steps, in order.

1. **Health check.** Run `curl -fsS -o /dev/null --max-time 10 -w '%{http_code}' <health_check_url, or base_url when there is none>`.
   - A non-zero exit, or a code that is not 2xx or 3xx, means the environment is down.
   - Then call `finish_run(run_id, summary="Environment down: <url> <code or curl error>")` with no case results, tell the user, and stop.
2. **Run each case** in the order `start_run` returned, step by step, in Claude in Chrome against `base_url`.
   - Screenshots taken only to find where to click or type: `scale: 0.5`.
   - One evidence screenshot per step, after the step's action: full size, `save_to_disk: true`. Keep its local path for `screenshot_path`.
   - Shared steps are already expanded in `steps`: run them like any other step, with the orders as given.
   - **Data-driven case** (the case has `parameters` and `data_rows`): run the whole case once per data row, in row order. Each row is one **iteration**, numbered from 0: the first row is `iteration` 0, the second is 1, and so on.
     - Before each iteration, replace every `{{param.<name>}}` in the preconditions, actions and expected results with that row's value for `<name>`.
     - A row value that holds `{{data.key}}` names a secret: resolve it as in step 3, just before that iteration uses it. In chat and in the results, write the row value as `{{data.key}}`, never the resolved secret.
     - Start each iteration from the case's preconditions again, as if it were a new case: open `base_url`, and sign out or reset what the previous iteration changed when the preconditions need it.
     - A failed or blocked iteration ends only that iteration. Go on with the next row: each row is checked on its own.
     - Steps 5 to 7 apply to each iteration: its own step statuses, its own diagnosis, its own evidence screenshots, and one `record_case_result` per iteration.
     - A case without `data_rows` runs once, with no `iteration`.
3. **Secrets.** `{{data.key}}` values in the context are secrets. Each data key may have a `description` that says what it is for: read it when a step's value is unclear.
   - Call `resolve_data(run_id, keys)` only for the keys the current case needs, just before you use them.
   - Never write a secret in chat, `actual_result`, `error` or `summary`.
4. **Files.** For `{{file.key}}`:
   - Call `get_test_file(run_id, key, case_id)`. `case_id` is optional; pass the current case's id when two cases in the run use the same key, otherwise the tool refuses the call with INVALID_REQUEST.
   - Run `mkdir -p "${TMPDIR:-/tmp}/tessio/<run_id>" && curl -fsS -o "${TMPDIR:-/tmp}/tessio/<run_id>/<file_name>" "<url>"`.
   - Attach the downloaded file with Claude in Chrome's `file_upload`.
5. **Step status.**
   - `passed`: the expected result was met.
   - `failed`: the expected result was not met.
   - `blocked`: the step cannot be executed (an app error, or a precondition is missing).
   - On the first `failed` or `blocked` step, stop the case and do not report the remaining steps; the server counts them as skipped.
   - `actual_result` and `error` are each at most 4000 characters.
   - `actual_result` says what the page showed; `error` says what differs from the expected result, in one or two sentences.
6. **Diagnose the failed or blocked step**, before recording, on that step only:
   - Note the page URL.
   - Call `read_console_messages` with `pattern: "error|exception|uncaught"`; keep up to 5 messages, each cut to 500 characters.
   - Call `read_network_requests` and keep up to 5 requests with a status of 400 or more (or no response): method, path, status, and the first 500 characters of the error body as `excerpt`.
   - Never copy a secret, token, cookie or password into these fields; drop query strings.
   - Pick one `suspected_cause` for the case and write a one-sentence `cause_reason` from what you saw:
     - `app_bug`: the app answered wrongly (a 5xx or unexpected 4xx, a console exception, a wrong value on the page).
     - `test_data`: the data did not fit (unknown account, expired card, missing record).
     - `environment`: the environment misbehaved (timeouts, the server down, a dependency unavailable).
     - `test_case`: the steps or the expected result no longer match the app (a renamed button, a changed flow).
     - `unknown`: none of the above is clear.
7. **Record the case.** After the case's last executed step, call once (once per iteration for a data-driven case):
   `record_case_result(run_id, case_id, status, duration_ms, steps=[{order, status, actual_result, error?, screenshot_path?, page_url?, console_errors?, failed_requests?}], suspected_cause?, cause_reason?)`.
   - Data-driven case: call `record_case_result` once per iteration, right after that iteration's last executed step, with `iteration=<row index>` (0 for the first row): `record_case_result(run_id, case_id, status, duration_ms, steps=[...], iteration=<row index>)`. `status`, `duration_ms` and `steps` are that iteration's only. Never send two results for the same iteration (`CASE_RESULT_EXISTS`); `ITERATION_OUT_OF_RANGE` means the index has no data row, so check your count. Tessio shows each iteration on its own and counts the worst one for the case.
   - Case `status`: `failed` if any step failed, else `blocked` if any step was blocked, else `passed`.
   - Pass `page_url`, `console_errors` and `failed_requests` only on the failed or blocked step, and `suspected_cause` with `cause_reason` only for a failed or blocked case.
   - Read nothing from the reply beyond `case_result_id` and do not repeat it; the hook uploads the screenshots.
8. **Finish.** Call `finish_run(run_id, summary)` with 2 to 5 plain sentences and no secrets.
   - Report the run status and `missing_screenshots` to the user. A missing screenshot of a data-driven case also names its `iteration`.
   - For a data-driven case, say how many iterations passed, failed and were blocked, and name the row values of each failed or blocked iteration (never a resolved secret).
   - If screenshots are missing, say the hook retries them the next time it runs.
   - A hook uploads your notes and actions of this run as its execution log, with secrets masked. Keep your notes between actions short and factual: testers read them.
