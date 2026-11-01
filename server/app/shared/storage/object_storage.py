from abc import ABC, abstractmethod
from datetime import timedelta

from app.shared.storage.object_head import ObjectHead
from app.shared.storage.signed_object_upload import SignedObjectUpload
from app.shared.storage.signed_upload import SignedUpload


class ObjectStorage(ABC):
    @abstractmethod
    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload: ...

    @abstractmethod
    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload: ...

    @abstractmethod
    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str: ...

    @abstractmethod
    async def head_object(self, key: str) -> ObjectHead | None: ...

    @abstractmethod
    async def list_keys(self, prefix: str) -> list[str]: ...

    @abstractmethod
    async def delete_object(self, key: str) -> None: ...

    @abstractmethod
    async def read_object(self, key: str) -> bytes | None: ...
