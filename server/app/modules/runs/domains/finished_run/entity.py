from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run.entity import Run
from app.shared.common import Entity


class FinishedRun(Entity):
    run: Run
    missing_screenshots: list[MissingScreenshot]
