START_RUN_DESCRIPTION = (
    "Start a test run for a story or a regression suite. Pass the story key, or suite with the suite name or id, "
    "and optionally an environment name, the case ids to run, "
    "or parent_run_id to re-run the failed and blocked cases of a finished run. "
    "The reply lists each case with its fixed version, preconditions and steps (shared steps already expanded). "
    "A data-driven case also lists its parameters and data_rows: run the steps once per row, "
    "with {{param.name}} replaced by the row's value. "
    "A suite run also names each case's story and lists the cases it skipped (not Ready or Needs review)."
)
RECORD_CASE_RESULT_DESCRIPTION = (
    "Record the result of one test case after its last step. "
    "For a data-driven case, record each data row separately with iteration set to the row's index (0 first). "
    "Pass each step's local screenshot file path in screenshot_path; never send image data. "
    "A Tessio hook uploads the screenshots after this call. "
    "On the failed or blocked step, pass page_url, console_errors and failed_requests, "
    "and pass suspected_cause with a one-sentence cause_reason for the case."
)
FINISH_RUN_DESCRIPTION = (
    "Finish a run after the last case is recorded. Tessio sets the run status from the recorded results, "
    "checks the uploaded screenshots and builds the report. The reply lists the screenshots that never arrived."
)
GET_FAILED_CASES_DESCRIPTION = "List the failed and blocked cases of a run, in run order."
