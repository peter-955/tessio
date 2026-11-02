CHECK_DRAFT_CASES_DESCRIPTION = (
    "Check up to 100 test cases before creating them, with the same rules as the spreadsheet import: "
    "story found, at most 100 steps, title at most 200 characters, texts at most 5000, duplicate titles, "
    "unknown AC codes. Creates nothing. Returns only the cases that have an issue, by index."
)
CREATE_DRAFT_CASES_DESCRIPTION = (
    "Create up to 100 test cases as Draft in the token's project, after the user confirmed them. "
    "All or nothing: a case with a problem from check_draft_cases refuses the whole call. "
    "Returns the new case codes in input order."
)
