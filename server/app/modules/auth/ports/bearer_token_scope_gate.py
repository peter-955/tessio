from abc import ABC, abstractmethod


class BearerTokenScopeGate(ABC):
    @abstractmethod
    async def refuse_on_session_route(self, authorization: str) -> None: ...
