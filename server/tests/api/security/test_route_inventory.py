from app.container import Container
from app.main import create_app
from app.shared.permissions import Capability, ProjectRole
from app.shared.permissions.role_capabilities import PROJECT_ROLE_CAPABILITIES
from tests.api.security.route_access import RouteAccess
from tests.api.security.route_catalog import SECURED_ROUTES
from tests.api.security.security_steps import list_application_routes

PUBLIC_ROUTES = {
    ("GET", "/api/health"),
    ("GET", "/api/health/ready"),
    ("GET", "/api/plugin/marketplace.json"),
    ("GET", "/api/plugin/{file_name}"),
    ("POST", "/api/auth/sign-in"),
    ("POST", "/api/auth/invites/{token}"),
    ("POST", "/api/auth/password/forgot"),
    ("POST", "/api/auth/password/reset"),
}
API_TOKEN_ROUTES = {
    ("POST", "/api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload"),
    ("POST", "/api/runs/{run_id}/log"),
    ("POST", "/mcp"),
}
PROJECT_ACCESSES = {RouteAccess.PROJECT_READ, RouteAccess.PROJECT_WRITE}


def test_every_route_of_the_application_is_classified(container: Container) -> None:
    application_routes = list_application_routes(create_app(container))

    catalog_routes = {route.key for route in SECURED_ROUTES}

    assert sorted(application_routes - catalog_routes) == []
    assert sorted(catalog_routes - application_routes) == []
    assert len(SECURED_ROUTES) == len(catalog_routes)


def test_only_the_expected_routes_are_public_or_use_api_tokens() -> None:
    assert {route.key for route in SECURED_ROUTES if route.access is RouteAccess.PUBLIC} == PUBLIC_ROUTES
    assert {route.key for route in SECURED_ROUTES if route.access is RouteAccess.API_TOKEN} == API_TOKEN_ROUTES


def test_every_project_and_workspace_route_names_its_capability() -> None:
    unnamed_routes = [
        route.key
        for route in SECURED_ROUTES
        if route.access in PROJECT_ACCESSES | {RouteAccess.WORKSPACE} and route.capability is None
    ]

    assert unnamed_routes == []


def test_every_project_route_is_scoped_by_its_path() -> None:
    unscoped_routes = [
        route.key
        for route in SECURED_ROUTES
        if route.access in PROJECT_ACCESSES and not route.path.startswith("/api/projects/{project_key}")
    ]

    assert unscoped_routes == []


def test_reads_need_a_viewer_capability_and_writes_need_more() -> None:
    viewer_capabilities = PROJECT_ROLE_CAPABILITIES[ProjectRole.VIEWER]
    misclassified_routes = [
        route.key
        for route in SECURED_ROUTES
        if (route.access is RouteAccess.PROJECT_READ and route.capability not in viewer_capabilities)
        or (
            route.access is RouteAccess.PROJECT_WRITE
            and isinstance(route.capability, Capability)
            and route.capability in viewer_capabilities
        )
    ]

    assert misclassified_routes == []
