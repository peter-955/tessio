from app.modules.jira.typing.enums import JiraCommentTrigger
from app.modules.projects import JiraPostResults


def is_posting_results(setting: JiraPostResults, trigger: JiraCommentTrigger) -> bool:
    if trigger is JiraCommentTrigger.SIGN_OFF:
        return setting is JiraPostResults.ON_SIGN_OFF
    return setting is JiraPostResults.EVERY_RUN
