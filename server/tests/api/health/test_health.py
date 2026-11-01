import asyncio

from fastapi import FastAPI
from httpx import AsyncClient

from app.modules.health import CheckReadinessUseCase
from app.modules.health.dependencies import get_check_readiness
from app.modules.health.ports.dependency_probe import DependencyProbe
from app.modules.health.typing.enums import DependencyStatus


class FixedDependencyProbe(DependencyProbe):
    def __init__(self, is_reachable: bool) -> None:
        self._is_reachable = is_reachable

    async def is_reachable(self) -> bool:
        return self._is_reachable


class RaisingDependencyProbe(DependencyProbe):
    async def is_reachable(self) -> bool:
        raise ConnectionError("dependency is down")


class SlowDependencyProbe(DependencyProbe):
    async def is_reachable(self) -> bool:
        await asyncio.sleep(5)
        return True


async def test_liveness_returns_ok(health_client: AsyncClient) -> None:
    response = await health_client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_reports_every_dependency_ok(health_client: AsyncClient) -> None:
    response = await health_client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"postgres": "ok", "redis": "ok"}}


async def test_readiness_names_the_failed_dependency(health_application: FastAPI, health_client: AsyncClient) -> None:
    health_application.dependency_overrides[get_check_readiness] = lambda: CheckReadinessUseCase(
        {"postgres": FixedDependencyProbe(is_reachable=True), "redis": FixedDependencyProbe(is_reachable=False)}
    )

    response = await health_client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "checks": {"postgres": "ok", "redis": "failed"}}


async def test_readiness_lists_the_unavailable_response_in_openapi(health_application: FastAPI) -> None:
    responses = health_application.openapi()["paths"]["/api/health/ready"]["get"]["responses"]

    assert "503" in responses


async def test_a_raising_probe_is_failed() -> None:
    report = await CheckReadinessUseCase({"redis": RaisingDependencyProbe()}).execute()

    assert report.checks == {"redis": DependencyStatus.FAILED}
    assert not report.is_ready


async def test_a_slow_probe_times_out_as_failed() -> None:
    use_case = CheckReadinessUseCase(
        {"postgres": FixedDependencyProbe(is_reachable=True), "redis": SlowDependencyProbe()}
    )

    started_at = asyncio.get_running_loop().time()
    report = await use_case.execute()
    elapsed_seconds = asyncio.get_running_loop().time() - started_at

    assert report.checks == {"postgres": DependencyStatus.OK, "redis": DependencyStatus.FAILED}
    assert elapsed_seconds < 3
