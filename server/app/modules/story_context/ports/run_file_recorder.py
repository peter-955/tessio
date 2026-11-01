from abc import ABC, abstractmethod

from app.modules.story_context.domains.run_file.entity import RunFile


class RunFileRecorder(ABC):
    @abstractmethod
    async def record(self, run_file: RunFile) -> None: ...
