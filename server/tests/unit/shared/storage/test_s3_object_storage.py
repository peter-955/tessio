import base64
import json
from collections.abc import Iterator
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from botocore.stub import Stubber
from mypy_boto3_s3 import S3Client

from app.shared.storage import ObjectHead, S3ObjectStorage, build_s3_client

BUCKET = "tessio"
INTERNAL_ENDPOINT = "http://rustfs:9000"
PUBLIC_ENDPOINT = "http://localhost:3208"


def build_client(endpoint_url: str) -> S3Client:
    return build_s3_client(endpoint_url, "eu-west-3", "test-access-key", "test-secret-key")


@pytest.fixture
def internal_client() -> S3Client:
    return build_client(INTERNAL_ENDPOINT)


@pytest.fixture
def storage(internal_client: S3Client) -> S3ObjectStorage:
    return S3ObjectStorage(internal_client, build_client(PUBLIC_ENDPOINT), BUCKET)


@pytest.fixture
def stubber(internal_client: S3Client) -> Iterator[Stubber]:
    with Stubber(internal_client) as active_stubber:
        yield active_stubber
        active_stubber.assert_no_pending_responses()


def test_signed_download_uses_the_public_host_for_five_minutes_as_an_attachment(storage: S3ObjectStorage) -> None:
    url = storage.create_signed_download("projects/p/test_file/f/report.pdf", timedelta(minutes=5), "report.pdf")

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    assert f"{parsed_url.scheme}://{parsed_url.netloc}" == PUBLIC_ENDPOINT
    assert parsed_url.path == f"/{BUCKET}/projects/p/test_file/f/report.pdf"
    assert query["X-Amz-Expires"] == ["300"]
    assert query["response-content-disposition"][0].startswith('attachment; filename="report.pdf"')


def test_signed_download_strips_quotes_from_the_file_name(storage: S3ObjectStorage) -> None:
    url = storage.create_signed_download("key", timedelta(minutes=5), 'na"me\\é.txt')

    disposition = parse_qs(urlparse(url).query)["response-content-disposition"][0]
    assert disposition == "attachment; filename=\"name.txt\"; filename*=UTF-8''na%22me%5C%C3%A9.txt"


def test_signed_upload_uses_the_public_host(storage: S3ObjectStorage) -> None:
    signed_upload = storage.create_signed_upload("projects/p/test_file/f/", 1024, timedelta(minutes=15), "text/csv")

    assert signed_upload.url.startswith(f"{PUBLIC_ENDPOINT}/{BUCKET}")
    assert "key" not in signed_upload.fields
    assert signed_upload.key_prefix == "projects/p/test_file/f/"


def test_signed_object_upload_is_bound_to_the_exact_key(storage: S3ObjectStorage) -> None:
    key = "projects/p/test_file/f/data-set.csv"

    signed_upload = storage.create_signed_object_upload(key, 1024, timedelta(minutes=15), "text/csv")

    policy = json.loads(base64.b64decode(signed_upload.fields["policy"]))
    assert signed_upload.url.startswith(f"{PUBLIC_ENDPOINT}/{BUCKET}")
    assert signed_upload.fields["key"] == key
    assert {"key": key} in policy["conditions"]
    assert not any(isinstance(condition, list) and condition[1] == "$key" for condition in policy["conditions"])
    assert ["content-length-range", 1, 1024] in policy["conditions"]


def test_storage_without_a_public_endpoint_signs_with_the_internal_client(internal_client: S3Client) -> None:
    storage = S3ObjectStorage(internal_client, internal_client, BUCKET)

    url = storage.create_signed_download("key", timedelta(minutes=5), "file.txt")

    assert url.startswith(f"{INTERNAL_ENDPOINT}/{BUCKET}/key")


async def test_head_object_returns_the_size_and_content_type(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_response(
        "head_object",
        {"ContentLength": 2048, "ContentType": "image/png"},
        {"Bucket": BUCKET, "Key": "projects/p/evidence/f/shot.png"},
    )

    assert await storage.head_object("projects/p/evidence/f/shot.png") == ObjectHead(
        size=2048, content_type="image/png"
    )


async def test_head_object_returns_none_when_the_object_is_missing(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_client_error("head_object", service_error_code="404", http_status_code=404)

    assert await storage.head_object("missing") is None


async def test_head_object_raises_other_errors(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_client_error("head_object", service_error_code="403", http_status_code=403)

    with pytest.raises(Exception, match="403"):
        await storage.head_object("forbidden")


async def test_list_keys_reads_every_page(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_response(
        "list_objects_v2",
        {"Contents": [{"Key": "projects/p/a"}], "IsTruncated": True, "NextContinuationToken": "next"},
        {"Bucket": BUCKET, "Prefix": "projects/p/"},
    )
    stubber.add_response(
        "list_objects_v2",
        {"Contents": [{"Key": "projects/p/b"}], "IsTruncated": False},
        {"Bucket": BUCKET, "Prefix": "projects/p/", "ContinuationToken": "next"},
    )

    assert await storage.list_keys("projects/p/") == ["projects/p/a", "projects/p/b"]


async def test_list_keys_of_an_empty_prefix_is_empty(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_response("list_objects_v2", {"IsTruncated": False}, {"Bucket": BUCKET, "Prefix": "nothing/"})

    assert await storage.list_keys("nothing/") == []


async def test_delete_object_deletes_the_key(storage: S3ObjectStorage, stubber: Stubber) -> None:
    stubber.add_response("delete_object", {}, {"Bucket": BUCKET, "Key": "projects/p/a"})

    await storage.delete_object("projects/p/a")
