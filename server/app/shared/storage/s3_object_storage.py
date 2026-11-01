import functools
from datetime import timedelta
from typing import TYPE_CHECKING
from urllib.parse import quote

import anyio.to_thread
from botocore.exceptions import ClientError

from app.shared.storage.object_head import ObjectHead
from app.shared.storage.object_storage import ObjectStorage
from app.shared.storage.signed_object_upload import SignedObjectUpload
from app.shared.storage.signed_upload import SignedUpload

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

MISSING_OBJECT_ERROR_CODES = frozenset({"404", "NoSuchKey", "NotFound"})
DEFAULT_CONTENT_TYPE = "application/octet-stream"


class S3ObjectStorage(ObjectStorage):
    def __init__(self, client: S3Client, signing_client: S3Client, bucket: str) -> None:
        self._client = client
        self._signing_client = signing_client
        self._bucket = bucket

    def create_signed_upload(
        self, key_prefix: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedUpload:
        signed_post = self._signing_client.generate_presigned_post(
            Bucket=self._bucket,
            Key=f"{key_prefix}${{filename}}",
            Conditions=[
                ["starts-with", "$Content-Type", content_type_prefix],
                ["content-length-range", 1, max_bytes],
            ],
            ExpiresIn=int(lifetime.total_seconds()),
        )
        fields = {name: str(value) for name, value in signed_post["fields"].items() if name != "key"}
        return SignedUpload(url=signed_post["url"], fields=fields, key_prefix=key_prefix)

    def create_signed_object_upload(
        self, key: str, max_bytes: int, lifetime: timedelta, content_type_prefix: str
    ) -> SignedObjectUpload:
        signed_post = self._signing_client.generate_presigned_post(
            Bucket=self._bucket,
            Key=key,
            Conditions=[
                ["starts-with", "$Content-Type", content_type_prefix],
                ["content-length-range", 1, max_bytes],
            ],
            ExpiresIn=int(lifetime.total_seconds()),
        )
        fields = {name: str(value) for name, value in signed_post["fields"].items()}
        return SignedObjectUpload(url=signed_post["url"], fields=fields)

    def create_signed_download(self, key: str, lifetime: timedelta, file_name: str) -> str:
        return self._signing_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ResponseContentDisposition": self._build_attachment_disposition(file_name),
            },
            ExpiresIn=int(lifetime.total_seconds()),
        )

    async def head_object(self, key: str) -> ObjectHead | None:
        try:
            head = await anyio.to_thread.run_sync(
                functools.partial(self._client.head_object, Bucket=self._bucket, Key=key)
            )
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in MISSING_OBJECT_ERROR_CODES:
                return None
            raise
        return ObjectHead(size=head["ContentLength"], content_type=head.get("ContentType") or DEFAULT_CONTENT_TYPE)

    async def list_keys(self, prefix: str) -> list[str]:
        return await anyio.to_thread.run_sync(functools.partial(self._list_keys_blocking, prefix))

    async def delete_object(self, key: str) -> None:
        await anyio.to_thread.run_sync(functools.partial(self._client.delete_object, Bucket=self._bucket, Key=key))

    async def read_object(self, key: str) -> bytes | None:
        try:
            response = await anyio.to_thread.run_sync(
                functools.partial(self._client.get_object, Bucket=self._bucket, Key=key)
            )
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in MISSING_OBJECT_ERROR_CODES:
                return None
            raise
        return await anyio.to_thread.run_sync(response["Body"].read)

    def _list_keys_blocking(self, prefix: str) -> list[str]:
        paginator = self._client.get_paginator("list_objects_v2")
        return [
            listed_object["Key"]
            for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix)
            for listed_object in page.get("Contents", [])
            if "Key" in listed_object
        ]

    def _build_attachment_disposition(self, file_name: str) -> str:
        ascii_name = "".join(
            character for character in file_name if character.isascii() and character.isprintable()
        ).translate(str.maketrans("", "", '"\\'))
        return f"attachment; filename=\"{ascii_name or 'file'}\"; filename*=UTF-8''{quote(file_name, safe='')}"
