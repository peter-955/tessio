from abc import ABC, abstractmethod

from app.modules.runs.domains.run_file.entity import RunFile


class RunFileRepository(ABC):
    @abstractmethod
    async def add(self, run_file: RunFile) -> None: ...
