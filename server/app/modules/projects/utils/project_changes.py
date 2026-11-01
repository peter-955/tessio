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
        }
    )
