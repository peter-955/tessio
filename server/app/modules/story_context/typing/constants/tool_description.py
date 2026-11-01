GET_STORY_CONTEXT_DESCRIPTION = (
    "Story, active acceptance criteria, Ready test cases at their current version, the test data they use, "
    "their file keys and the environments. Secrets appear only as {{data.key}}: use resolve_data during a run."
)
RESOLVE_DATA_DESCRIPTION = (
    "Secret values for keys used by your own running run, for that run's environment. "
    "Every call is audited. Never write the values anywhere."
)
GET_TEST_FILE_DESCRIPTION = (
    "A 5-minute download link and file name for a {{file.key}} of a case in your running run. "
    "Pass case_id when several cases use the same key."
)
