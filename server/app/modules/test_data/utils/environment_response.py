from app.modules.test_data.domains.environment.entity import Environment
from app.modules.test_data.models.environment_response import EnvironmentResponse


def build_environment_response(environment: Environment) -> EnvironmentResponse:
    return EnvironmentResponse(
        id=environment.id,
        name=environment.name,
        base_url=environment.base_url,
        health_check_url=environment.health_check_url,
        is_archived=environment.is_archived,
        archived_at=environment.archived_at,
        created_at=environment.created_at,
    )
