from app.modules.projects.domains.project.entity import Project
from app.modules.projects.domains.project_changes.entity import ProjectChanges


def apply_project_changes(project: Project, changes: ProjectChanges) -> Project:
    return project.model_copy(
        update={
            "name": project.name if changes.name is None else changes.name.strip(),
            "description": project.description if changes.description is None else changes.description.strip() or None,
            "jira_board_id": project.jira_board_id if changes.jira_board_id is None else changes.jira_board_id,
            "allowed_file_types": project.allowed_file_types
            if changes.allowed_file_types is None
            else list(dict.fromkeys(changes.allowed_file_types)),
            "require_separate_reviewer": project.require_separate_reviewer
            if changes.require_separate_reviewer is None
            else changes.require_separate_reviewer,
            "jira_bug_issue_type": project.jira_bug_issue_type
            if changes.jira_bug_issue_type is None
            else changes.jira_bug_issue_type.strip(),
            "jira_post_results": project.jira_post_results
            if changes.jira_post_results is None
            else changes.jira_post_results,
        }
    )
