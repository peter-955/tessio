import asyncio
from collections.abc import Mapping

from app.modules.health.domains.readiness.entity import ReadinessReport
from app.modules.health.ports.dependency_probe import DependencyProbe
from app.modules.health.typing.constants.health import READINESS_TIMEOUT_SECONDS
from app.modules.health.typing.enums import DependencyStatus
from app.shared.logging import get_logger

log = get_logger(__name__)


class CheckReadinessUseCase:
    def __init__(self, probes: Mapping[str, DependencyProbe]) -> None:
        self._probes = probes

    async def execute(self) -> ReadinessReport:
        names = list(self._probes)
        statuses = await asyncio.gather(*(self._check(name, self._probes[name]) for name in names))
        return ReadinessReport(checks=dict(zip(names, statuses, strict=True)))

    async def _check(self, name: str, probe: DependencyProbe) -> DependencyStatus:
        try:
            async with asyncio.timeout(READINESS_TIMEOUT_SECONDS):
                is_reachable = await probe.is_reachable()
        except Exception:
            log.warning("readiness.check_failed", extra={"dependency": name})
            return DependencyStatus.FAILED
        if not is_reachable:
            log.warning("readiness.check_failed", extra={"dependency": name})
            return DependencyStatus.FAILED
        return DependencyStatus.OK
