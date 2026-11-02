import functools
from typing import TYPE_CHECKING

import anyio.to_thread

from app.modules.reports.ports.report_file_writer import ReportFileWriter

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class S3ReportFileWriter(ReportFileWriter):
    def __init__(self, client: S3Client, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    async def write(self, key: str, content: bytes, content_type: str) -> None:
        await anyio.to_thread.run_sync(
            functools.partial(
                self._client.put_object, Bucket=self._bucket, Key=key, Body=content, ContentType=content_type
            )
        )
