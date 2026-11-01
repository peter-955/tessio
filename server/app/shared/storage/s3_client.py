from typing import TYPE_CHECKING

import boto3
from botocore.config import Config

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def build_s3_client(
    endpoint_url: str | None, region: str, access_key_id: str | None, secret_access_key: str | None
) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
