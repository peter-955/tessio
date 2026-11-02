RAISE_GAPS_DESCRIPTION = (
    "File new gaps on a story in one call; each gap is routed to the role that can answer it. "
    "target_ref is the AC code (AC2), the case code (TC-12) or null for the story."
)
GET_OPEN_GAPS_DESCRIPTION = (
    "List the open gaps of a story and whether it is ready to test. "
    "target_ref is the AC code (AC2), the case code (TC-12) or null for the story. "
    "Each gap names who must answer it: assignee_name, or assignee_role for a role queue; "
    "is_assignee_deactivated marks an assignee who can no longer answer, so the gap needs reassigning."
)
GET_MY_GAPS_DESCRIPTION = (
    "List the open gaps assigned to you or to your role queue in this project, high severity first, "
    "optionally for one story. Each gap comes with the text of the AC or case it targets and up to three "
    "answered gaps with similar questions (same story first). Also lists each story's open gap count and "
    "the members a gap can be reassigned to, and test_data_url (the Test data page) when a gap is about "
    "missing test data."
)
ANSWER_GAP_DESCRIPTION = (
    "Answer an open gap and resolve it, as the Answer button does. Save only an answer the person confirmed. "
    "Replies with the story's open gap count and whether it is ready to test."
)
REASSIGN_GAP_DESCRIPTION = (
    "Reassign an open gap to an active member (assignee_user_id) or to a role queue (assignee_role); "
    "give exactly one. Viewers cannot be assignees."
)
