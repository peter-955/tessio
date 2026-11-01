#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import TypedDict

PENDING_UPLOADS_FILE = Path.home() / ".tessio" / "pending-uploads.jsonl"
RETRYABLE_STATUS_PREFIXES = ("000", "5")
CONTENT_TYPE_BY_SUFFIX = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
URL_VARIABLE_NAMES = ("CLAUDE_PLUGIN_OPTION_TESSIO_URL", "TESSIO_URL")
TOKEN_VARIABLE_NAMES = ("CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN", "TESSIO_TOKEN")
MISSING_SETTINGS_MESSAGE = (
    "Tessio hook: set the plugin options tessio_url and tessio_token "
    "(CLAUDE_PLUGIN_OPTION_TESSIO_URL and CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN), "
    "or TESSIO_URL and TESSIO_TOKEN, to upload screenshots."
)
INVALID_INPUT_MESSAGE = "Tessio hook: the hook input is not valid JSON, so no screenshots were uploaded."


class PendingUpload(TypedDict):
    path: str
    order: int
    run_id: str
    case_result_id: str


class SignedUpload(TypedDict):
    url: str
    keyPrefix: str
    fields: dict[str, str]


def read_setting(variable_names: tuple[str, ...]) -> str | None:
    for variable_name in variable_names:
        value = os.environ.get(variable_name, "")
        if value:
            return value
    return None


def resolve_settings() -> tuple[str, str] | None:
    url = read_setting(URL_VARIABLE_NAMES)
    token = read_setting(TOKEN_VARIABLE_NAMES)
    if url is None or token is None:
        return None
    return url.rstrip("/"), token


def read_response_text(tool_response: object) -> str | None:
    if isinstance(tool_response, dict):
        if tool_response.get("isError") is True:
            return None
        tool_response = tool_response.get("content")
    if isinstance(tool_response, str):
        return tool_response
    if not isinstance(tool_response, list):
        return None
    for block in tool_response:
        if not isinstance(block, dict) or block.get("type") != "text":
            return None
        text = block.get("text")
        return text if isinstance(text, str) else None
    return None


def read_case_result_id(tool_response: object) -> str | None:
    text = read_response_text(tool_response)
    if text is None:
        return None
    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            return None
        case_result_id = parsed["case_result_id"]
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
    return case_result_id if isinstance(case_result_id, str) else None


def build_uploads(payload: object) -> list[PendingUpload]:
    if not isinstance(payload, dict):
        return []
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
    run_id = tool_input.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        return []
    case_result_id = read_case_result_id(payload.get("tool_response"))
    if case_result_id is None:
        return []
    steps = tool_input.get("steps")
    if not isinstance(steps, list):
        return []
    uploads: list[PendingUpload] = []
    for step in steps:
        if not isinstance(step, dict) or "order" not in step:
            continue
        order = step["order"]
        screenshot_path = step.get("screenshot_path")
        if isinstance(order, int) and isinstance(screenshot_path, str) and screenshot_path:
            uploads.append(
                {"path": screenshot_path, "order": order, "run_id": run_id, "case_result_id": case_result_id}
            )
    return uploads


def parse_signed_upload(value: object) -> SignedUpload | None:
    if not isinstance(value, dict):
        return None
    url = value.get("url")
    key_prefix = value.get("keyPrefix")
    fields = value.get("fields")
    if not isinstance(url, str) or not isinstance(key_prefix, str) or not isinstance(fields, dict):
        return None
    return {"url": url, "keyPrefix": key_prefix, "fields": {str(name): str(field) for name, field in fields.items()}}


def request_signed_upload(url: str, token: str, run_id: str, case_result_id: str) -> SignedUpload | None:
    request = urllib.request.Request(
        f"{url}/api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload",
        method="POST",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return parse_signed_upload(json.loads(response.read()))
    except (OSError, ValueError):
        return None


def compress_screenshot(source: Path, work_directory: Path) -> tuple[Path, str]:
    if source.suffix.lower() in {".jpg", ".jpeg"}:
        return source, "image/jpeg"
    if sys.platform == "darwin" and shutil.which("sips"):
        target = work_directory / f"{source.stem}.jpg"
        command = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", str(source), "--out", str(target)]
        if subprocess.run(command, capture_output=True, check=False).returncode == 0:
            return target, "image/jpeg"
    if shutil.which("cwebp"):
        target = work_directory / f"{source.stem}.webp"
        command = ["cwebp", "-quiet", "-q", "70", str(source), "-o", str(target)]
        if subprocess.run(command, capture_output=True, check=False).returncode == 0:
            return target, "image/webp"
    return source, CONTENT_TYPE_BY_SUFFIX.get(source.suffix.lower(), "image/png")


def send_upload(upload: PendingUpload, signed_upload: SignedUpload | None, work_directory: Path) -> str:
    source = Path(upload["path"]).expanduser()
    if not source.is_file():
        return "missing"
    if signed_upload is None:
        return "000"
    file_to_send, content_type = compress_screenshot(source, work_directory / str(upload["order"]))
    command = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "60", "-X", "POST"]
    command += [signed_upload["url"], "-F", f"key={signed_upload['keyPrefix']}{upload['order']}{file_to_send.suffix}"]
    command += ["-F", f"Content-Type={content_type}"]
    for name, value in signed_upload["fields"].items():
        command += ["-F", f"{name}={value}"]
    command += ["-F", f"file=@{file_to_send}"]
    return subprocess.run(command, capture_output=True, text=True, check=False).stdout.strip() or "000"


def parse_pending_upload(value: object) -> PendingUpload | None:
    if not isinstance(value, dict):
        return None
    path = value.get("path")
    order = value.get("order")
    run_id = value.get("run_id")
    case_result_id = value.get("case_result_id")
    if not isinstance(path, str) or not isinstance(order, int):
        return None
    if not isinstance(run_id, str) or not isinstance(case_result_id, str):
        return None
    return {"path": path, "order": order, "run_id": run_id, "case_result_id": case_result_id}


def read_pending_uploads() -> list[PendingUpload]:
    if not PENDING_UPLOADS_FILE.is_file():
        return []
    try:
        pending_text = PENDING_UPLOADS_FILE.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    uploads: list[PendingUpload] = []
    for line in pending_text.splitlines():
        if not line.strip():
            continue
        try:
            upload = parse_pending_upload(json.loads(line))
        except ValueError:
            continue
        if upload is not None:
            uploads.append(upload)
    return uploads


def write_pending_uploads(uploads: list[PendingUpload]) -> None:
    PENDING_UPLOADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_UPLOADS_FILE.write_text("".join(json.dumps(upload) + "\n" for upload in uploads), encoding="utf-8")


def main() -> int:
    settings = resolve_settings()
    if settings is None:
        print(MISSING_SETTINGS_MESSAGE, file=sys.stderr)
        return 0
    url, token = settings
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        print(INVALID_INPUT_MESSAGE, file=sys.stderr)
        return 0
    uploads = read_pending_uploads() + build_uploads(payload)
    signed_uploads: dict[tuple[str, str], SignedUpload | None] = {}
    still_pending: list[PendingUpload] = []
    with tempfile.TemporaryDirectory() as work_directory:
        for upload in uploads:
            case_key = (upload["run_id"], upload["case_result_id"])
            if case_key not in signed_uploads:
                signed_uploads[case_key] = request_signed_upload(url, token, *case_key)
            step_directory = Path(work_directory) / str(upload["order"])
            step_directory.mkdir(exist_ok=True)
            status = send_upload(upload, signed_uploads[case_key], Path(work_directory))
            if status.startswith(RETRYABLE_STATUS_PREFIXES):
                still_pending.append(upload)
    write_pending_uploads(still_pending)
    return 0


if __name__ == "__main__":
    sys.exit(main())
