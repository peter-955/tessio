import json
from pathlib import Path

from app.commands.export_openapi import build_openapi_document, export_openapi
from app.container import Container
from app.main import create_app
from app.shared.typing.enums import ErrorCode


def _read_schemas(document: dict[str, object]) -> dict[str, object]:
    components = document["components"]
    assert isinstance(components, dict)
    schemas = components["schemas"]
    assert isinstance(schemas, dict)
    return schemas


def _read_mapping(parent: dict[str, object], key: str) -> dict[str, object]:
    value = parent[key]
    assert isinstance(value, dict)
    return value


def _contains_key(value: object, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(child, key) for child in value)
    return False


async def test_error_code_schema_lists_every_error_code(container: Container) -> None:
    document = build_openapi_document(create_app(container))

    error_code_schema = _read_mapping(_read_schemas(document), "ErrorCode")

    assert error_code_schema["enum"] == [code.value for code in ErrorCode]
    assert error_code_schema["type"] == "string"


async def test_error_response_schema_references_error_code(container: Container) -> None:
    document = build_openapi_document(create_app(container))

    error_response_schema = _read_mapping(_read_schemas(document), "ErrorResponse")
    properties = _read_mapping(error_response_schema, "properties")
    required = error_response_schema["required"]

    assert properties["code"] == {"$ref": "#/components/schemas/ErrorCode"}
    assert _read_mapping(properties, "message")["type"] == "string"
    assert isinstance(required, list)
    assert "message" in required
    assert "code" in required


async def test_document_lists_the_api_paths(container: Container) -> None:
    document = build_openapi_document(create_app(container))

    assert "/api/auth/sign-in" in _read_mapping(document, "paths")


async def test_document_has_no_inline_definitions(container: Container) -> None:
    document = build_openapi_document(create_app(container))

    assert not _contains_key(document, "$defs")


async def test_export_writes_formatted_json(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "openapi.json"

    await export_openapi(output)

    content = output.read_text(encoding="utf-8")
    document = json.loads(content)
    assert content.endswith("}\n")
    assert content.startswith('{\n  "openapi"')
    assert "ErrorResponse" in _read_schemas(document)
