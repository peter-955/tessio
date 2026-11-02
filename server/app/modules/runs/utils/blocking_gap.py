from app.modules.runs.domains.blocking_gap.entity import BlockingGap
from app.modules.runs.typing.constants.blocking_gap import ROLE_LABELS
from app.modules.runs.typing.constants.run import MAX_BLOCKING_GAP_QUESTION_LENGTH


def describe_blocking_gap(gap: BlockingGap) -> str:
    if gap.assignee_name is not None:
        assignee = gap.assignee_name
    elif gap.assignee_role is not None:
        assignee = f"the {ROLE_LABELS[gap.assignee_role]} role"
    else:
        assignee = "nobody"
    question = " ".join(gap.question.split())
    if len(question) > MAX_BLOCKING_GAP_QUESTION_LENGTH:
        question = f"{question[: MAX_BLOCKING_GAP_QUESTION_LENGTH - 1].rstrip()}…"
    return f"{gap.story_jira_key} gap {gap.gap_id} (assigned to {assignee}): {question}"
