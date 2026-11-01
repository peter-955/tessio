from datetime import timedelta

from app.shared.storage import ObjectHead, ObjectStorage, SignedObjectUpload, SignedUpload

SIGNED_UPLOAD_URL = "https://storage.test/tessio"


class InMemoryObjectStorage(ObjectStorage):
    def __init__(self) -> None:
        self.contents: dict[str, bytes] = {}

    def put(self, key: str, content: bytes) -> None:
        self.contents[key] = content

    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload:
        return SignedUpload(url=SIGNED_UPLOAD_URL, fields={"policy": "signed"}, key_prefix=key_prefix)

    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload:
        return SignedObjectUpload(url=SIGNED_UPLOAD_URL, fields={"key": key, "policy": "signed"})

    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str:
        return f"{SIGNED_UPLOAD_URL}/{key}"

    async def head_object(self, key: str) -> ObjectHead | None:
        content = self.contents.get(key)
        return None if content is None else ObjectHead(size=len(content), content_type="text/plain")

    async def list_keys(self, prefix: str) -> list[str]:
        return sorted(key for key in self.contents if key.startswith(prefix))

    async def delete_object(self, key: str) -> None:
        self.contents.pop(key, None)

    async def read_object(self, key: str) -> bytes | None:
        return self.contents.get(key)
