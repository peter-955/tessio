from abc import ABC, abstractmethod
from datetime import datetime


class TotpAuthenticator(ABC):
    @abstractmethod
    def generate_key(self) -> str: ...

    @abstractmethod
    def build_setup_uri(self, key: str, account_name: str) -> str: ...

    @abstractmethod
    def find_time_step(self, key: str, code: str, now: datetime) -> int | None: ...
