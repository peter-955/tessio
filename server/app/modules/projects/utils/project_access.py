from app.modules.projects.domains.project.entity import Project
from app.shared.permissions import ProjectAccess, ProjectRole


def build_project_access(project: Project, role: ProjectRole | None) -> ProjectAccess:
    return ProjectAccess(project_id=project.id, project_key=project.key, role=role, is_archived=project.is_archived)
