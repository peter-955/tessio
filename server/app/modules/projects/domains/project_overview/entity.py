from app.modules.projects.domains.project.entity import Project
from app.shared.common import Entity
from app.shared.permissions import ProjectAccess


class ProjectOverview(Entity):
    project: Project
    access: ProjectAccess
