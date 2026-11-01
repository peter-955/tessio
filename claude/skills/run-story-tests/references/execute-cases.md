# Execute the cases of a started run

Use the reply of `start_run`: `run_id`, `base_url`, `health_check_url` and the cases with their steps, in order.

1. **Health check.** Run `curl -fsS -o /dev/null --max-time 10 -w '%{http_code}' <health_check_url, or base_url when there is none>`.
   - A non-zero exit, or a code that is not 2xx or 3xx, means the environment is down.
   - Then call `finish_run(run_id, summary="Environment down: <url> <code or curl error>")` with no case results, tell the user, and stop.
2. **Run each case** in the order `start_run` returned, step by step, in Claude in Chrome against `base_url`.
   - Screenshots taken only to find where to click or type: `scale: 0.5`.
   - One evidence screenshot per step, after the step's action: full size, `save_to_disk: true`. Keep its local path for `screenshot_path`.
3. **Secrets.** `{{data.key}}` values in the context are secrets.
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
6. **Record the case.** After the case's last executed step, call once:
   `record_case_result(run_id, case_id, status, duration_ms, steps=[{order, status, actual_result, error?, screenshot_path?}])`.
   - Case `status`: `failed` if any step failed, else `blocked` if any step was blocked, else `passed`.
   - Read nothing from the reply beyond `case_result_id` and do not repeat it; the hook uploads the screenshots.
7. **Finish.** Call `finish_run(run_id, summary)` with 2 to 5 plain sentences and no secrets.
   - Report the run status and `missing_screenshots` to the user.
   - If screenshots are missing, say the hook retries them the next time it runs.
