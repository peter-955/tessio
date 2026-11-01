import json
from pathlib import Path

from pydantic import JsonValue

ADF_FIXTURES_DIRECTORY = Path(__file__).parents[2] / "fixtures" / "adf"


def load_adf_fixture(name: str) -> JsonValue:
    loaded: JsonValue = json.loads((ADF_FIXTURES_DIRECTORY / f"{name}.json").read_text(encoding="utf-8"))
    return loaded
