from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.transport_security import TransportSecuritySettings

from app.api.error_handlers import register_error_handlers
from app.api.origin_check import OriginCheckMiddleware
from app.config import get_settings
from app.container import Container
from app.modules.ai_harness import ai_harness_router
from app.modules.api_tokens import api_tokens_router
from app.modules.auth import auth_router, me_router, users_router
from app.modules.failures import failures_router
from app.modules.files import files_router
from app.modules.gaps import gaps_router
from app.modules.health import health_router
from app.modules.insights import insights_router
from app.modules.integrations import chat_channels_router, webhooks_router
from app.modules.jira import jira_router
from app.modules.labels import labels_router
from app.modules.live_events import live_events_router
from app.modules.notifications import notification_preferences_router, notifications_router
from app.modules.plans import plans_router
from app.modules.plugin import plugin_router
from app.modules.projects import projects_router
from app.modules.reports import reports_router
from app.modules.run_logs import run_logs_router
from app.modules.runs import manual_runs_router, runs_router
from app.modules.shared_steps import shared_steps_router
from app.modules.stories import stories_router
from app.modules.story_context import story_context_router
from app.modules.suites import suites_router
from app.modules.test_cases import test_cases_router
from app.modules.test_data import test_data_router
from app.shared.logging import configure_logging


def create_app(container: Container) -> FastAPI:
    _ = container.plugin_bundle
    mcp_app = container.mcp_server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with container.mcp_server.session_manager.run():
            yield
        await container.close()

    application = FastAPI(title="Tessio", lifespan=lifespan)
    application.state.container = container
    application.add_middleware(OriginCheckMiddleware, allowed_origins=container.allowed_origins)
    register_error_handlers(application)
    application.include_router(auth_router)
    application.include_router(users_router)
    application.include_router(me_router)
    application.include_router(live_events_router)
    application.include_router(runs_router)
    application.include_router(manual_runs_router)
    application.include_router(run_logs_router)
    application.include_router(story_context_router)
    application.include_router(failures_router)
    application.include_router(projects_router)
    application.include_router(api_tokens_router)
    application.include_router(files_router)
    application.include_router(jira_router)
    application.include_router(test_data_router)
    application.include_router(stories_router)
    application.include_router(test_cases_router)
    application.include_router(labels_router)
    application.include_router(shared_steps_router)
    application.include_router(suites_router)
    application.include_router(plans_router)
    application.include_router(chat_channels_router)
    application.include_router(webhooks_router)
    application.include_router(reports_router)
    application.include_router(notifications_router)
    application.include_router(notification_preferences_router)
    application.include_router(gaps_router)
    application.include_router(insights_router)
    application.include_router(health_router)
    application.include_router(plugin_router)
    application.include_router(ai_harness_router)
    application.router.routes.extend(mcp_app.routes)
    return application


def create_production_app() -> FastAPI:
    settings = get_settings()
    configure_logging(
        settings.observability.log_level, settings.observability.sentry_dsn, settings.observability.sentry_environment
    )
    return create_app(Container(settings))
