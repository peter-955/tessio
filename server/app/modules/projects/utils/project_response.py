from app.modules.projects.domains.project_overview.entity import ProjectOverview
from app.modules.projects.models.project_response import ProjectResponse
from app.shared.permissions import Capability, list_capabilities


def build_project_response(overview: ProjectOverview) -> ProjectResponse:
    project = overview.project
    capabilities = list_capabilities(overview.access)
    return ProjectResponse(
        id=project.id,
        key=project.key,
        name=project.name,
        description=project.description,
        jira_project_key=project.jira_project_key,
        jira_board_id=project.jira_board_id,
        is_linked_to_jira=project.is_linked_to_jira,
        allowed_file_types=project.allowed_file_types,
        is_archived=project.is_archived,
        archived_at=project.archived_at,
        created_at=project.created_at,
        default_environment_id=project.default_environment_id,
        require_separate_reviewer=project.require_separate_reviewer,
        jira_bug_issue_type=project.jira_bug_issue_type,
        jira_post_results=project.jira_post_results,
        my_role=overview.access.role,
        capabilities=[capability for capability in Capability if capability in capabilities],
    )
