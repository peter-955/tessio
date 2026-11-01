from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class Transaction(ABC):
    @abstractmethod
    def begin(self) -> AbstractAsyncContextManager[None]: ...
