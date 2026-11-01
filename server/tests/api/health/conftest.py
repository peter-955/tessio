from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.container import Container
from app.modules.health import CheckReadinessUseCase, health_router
from app.modules.health.dependencies import get_check_readiness
from app.modules.health.infrastructure import PostgresReadinessProbe, RedisReadinessProbe


@pytest.fixture
def health_application(container: Container, redis_url: str) -> FastAPI:
    application = FastAPI()
    application.include_router(health_router)
    application.dependency_overrides[get_check_readiness] = lambda: CheckReadinessUseCase(
        {"postgres": PostgresReadinessProbe(container.database), "redis": RedisReadinessProbe(redis_url)}
    )
    return application


@pytest.fixture
async def health_client(health_application: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=health_application), base_url="https://testserver") as client:
        yield client
