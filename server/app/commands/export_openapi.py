import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import TypeAdapter

from app.api.error_response import ErrorResponse
from app.config import (
    ClientSettings,
    DatabaseSettings,
    MailSettings,
    QueueSettings,
    SecuritySettings,
    Settings,
    StorageSettings,
)
from app.container import Container
from app.main import create_app

DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[3] / "client" / "src" / "lib" / "api" / "openapi.json"
EXPORT_DATABASE_URL = "postgresql+asyncpg://export:export@localhost:5432/export"
SCHEMA_REFERENCE_TEMPLATE = "#/components/schemas/{model}"


def build_export_settings() -> Settings:
    return Settings(
        database=DatabaseSettings.model_validate({"DATABASE_URL": EXPORT_DATABASE_URL}),
        mail=MailSettings(),
        queue=QueueSettings(),
        security=SecuritySettings.model_validate({"TESSIO_ENCRYPTION_KEY": base64.b64encode(bytes(32)).decode()}),
        storage=StorageSettings.model_validate({"S3_BUCKET": "export"}),
        client=ClientSettings(),
    )


def _get_or_create_mapping(parent: dict[str, object], key: str) -> dict[str, object]:
    value = parent.get(key)
    if isinstance(value, dict):
        return value
    mapping: dict[str, object] = {}
    parent[key] = mapping
    return mapping


def add_error_schemas(document: dict[str, object]) -> None:
    schema: dict[str, object] = TypeAdapter(ErrorResponse).json_schema(
        by_alias=True, ref_template=SCHEMA_REFERENCE_TEMPLATE
    )
    definitions = schema.pop("$defs", {})
    schemas = _get_or_create_mapping(_get_or_create_mapping(document, "components"), "schemas")
    if isinstance(definitions, dict):
        for name, definition in definitions.items():
            if isinstance(name, str):
                schemas[name] = definition
    schemas["ErrorResponse"] = schema


def build_openapi_document(application: FastAPI) -> dict[str, object]:
    document: dict[str, object] = dict(application.openapi())
    add_error_schemas(document)
    return document


def write_document(output: Path, document: dict[str, object]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


async def export_openapi(output: Path) -> None:
    container = Container(build_export_settings())
    try:
        document = build_openapi_document(create_app(container))
    finally:
        await container.close()
    await asyncio.to_thread(write_document, output, document)
    sys.stdout.write(f"{output}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the Tessio OpenAPI document for the client.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    arguments = parser.parse_args()
    asyncio.run(export_openapi(arguments.output))


if __name__ == "__main__":
    main()
