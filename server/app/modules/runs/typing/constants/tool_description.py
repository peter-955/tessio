START_RUN_DESCRIPTION = (
    "Start a test run for a story. Pass the story key, and optionally an environment name, the case ids to run, "
    "or parent_run_id to re-run the failed and blocked cases of a finished run. "
    "The reply lists each case with its fixed version, preconditions and steps."
)
RECORD_CASE_RESULT_DESCRIPTION = (
    "Record the result of one test case after its last step. "
    "Pass each step's local screenshot file path in screenshot_path; never send image data. "
    "A Tessio hook uploads the screenshots after this call."
)
FINISH_RUN_DESCRIPTION = (
    "Finish a run after the last case is recorded. Tessio sets the run status from the recorded results, "
    "checks the uploaded screenshots and builds the report. The reply lists the screenshots that never arrived."
)
GET_FAILED_CASES_DESCRIPTION = "List the failed and blocked cases of a run, in run order."
