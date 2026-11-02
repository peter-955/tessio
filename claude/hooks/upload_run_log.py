#!/usr/bin/env python3
"""Upload Claude's log of a Tessio run after finish_run.

Reads this run's part of Claude Code's session log (transcript_path), keeps Claude's notes and actions,
masks the secret values resolve_data returned, drops images, cuts long texts and sends it once to
POST /api/runs/{run_id}/log. A failed upload waits in ~/.tessio/pending-run-logs/ and is retried on the
next run of this hook. Only the standard library is used, and the hook always exits 0.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PENDING_LOGS_DIRECTORY = Path.home() / ".tessio" / "pending-run-logs"
URL_VARIABLE_NAMES = ("CLAUDE_PLUGIN_OPTION_TESSIO_URL", "TESSIO_URL")
TOKEN_VARIABLE_NAMES = ("CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN", "TESSIO_TOKEN")
TOOL_SUFFIX_START_RUN = "start_run"
TOOL_SUFFIX_FINISH_RUN = "finish_run"
TOOL_SUFFIX_RESOLVE_DATA = "resolve_data"
MASKED_VALUE = "••••"
SCREENSHOT_PLACEHOLDER = "[screenshot]"
TRUNCATED_INPUT_KEY = "truncated"
MAX_ENTRIES = 3000
MAX_TEXT_LENGTH = 4000
MAX_PENDING_LOGS = 20
REQUEST_TIMEOUT_SECONDS = 60
MISSING_SETTINGS_MESSAGE = (
    "Tessio log hook: set the plugin options tessio_url and tessio_token, "
    "or TESSIO_URL and TESSIO_TOKEN, to upload the run log."
)

Json = object


def read_setting(variable_names: Tuple[str, ...]) -> Optional[str]:
    for variable_name in variable_names:
        value = os.environ.get(variable_name, "")
        if value:
            return value
    return None


def clean(text: str) -> str:
    return text.replace("\x00", "")


def cut(text: str) -> str:
    return text[:MAX_TEXT_LENGTH]


def parse_time(value: Json) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_transcript(path: Path) -> List[Dict[str, Json]]:
    lines: List[Dict[str, Json]] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as transcript:
            for line in transcript:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict) and entry.get("type") in ("assistant", "user") and not entry.get("isSidechain"):
                    lines.append(entry)
    except OSError:
        return []
    return lines


def content_blocks(entry: Dict[str, Json]) -> List[Dict[str, Json]]:
    message = entry.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    return [block for block in content if isinstance(block, dict)]


def result_text(block: Dict[str, Json]) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    parts: List[str] = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text" and isinstance(part.get("text"), str):
                parts.append(str(part["text"]))
            elif part.get("type") == "image":
                parts.append(SCREENSHOT_PLACEHOLDER)
    return "\n".join(parts)


def find_slice(lines: List[Dict[str, Json]], run_id: str) -> Optional[Tuple[int, int]]:
    tool_names: Dict[str, str] = {}
    start_use_line: Dict[str, int] = {}
    start: Optional[int] = None
    end: Optional[int] = None
    for index, entry in enumerate(lines):
        for block in content_blocks(entry):
            if block.get("type") == "tool_use":
                name = str(block.get("name", ""))
                tool_use_id = str(block.get("id", ""))
                tool_names[tool_use_id] = name
                if name.endswith(TOOL_SUFFIX_START_RUN):
                    start_use_line[tool_use_id] = index
                tool_input = block.get("input")
                if (
                    start is not None
                    and name.endswith(TOOL_SUFFIX_FINISH_RUN)
                    and isinstance(tool_input, dict)
                    and tool_input.get("run_id") == run_id
                ):
                    end = index
            elif block.get("type") == "tool_result":
                tool_use_id = str(block.get("tool_use_id", ""))
                if tool_use_id in start_use_line and run_id in result_text(block):
                    start = start_use_line[tool_use_id]
                    end = None
    if start is None:
        return None
    return start, len(lines) - 1 if end is None else end


def collect_secrets(lines: List[Dict[str, Json]]) -> List[str]:
    resolve_ids = set()
    secrets: List[str] = []
    for entry in lines:
        for block in content_blocks(entry):
            if block.get("type") == "tool_use" and str(block.get("name", "")).endswith(TOOL_SUFFIX_RESOLVE_DATA):
                resolve_ids.add(str(block.get("id", "")))
            elif block.get("type") == "tool_result" and str(block.get("tool_use_id", "")) in resolve_ids:
                try:
                    values = json.loads(result_text(block)).get("values", {})
                except (ValueError, AttributeError):
                    continue
                if isinstance(values, dict):
                    secrets.extend(str(value) for value in values.values() if str(value))
    return sorted(set(secrets), key=len, reverse=True)


def mask(value: Json, secrets: List[str]) -> Json:
    if isinstance(value, str):
        masked = value
        for secret in secrets:
            masked = masked.replace(secret, MASKED_VALUE)
        return clean(masked)
    if isinstance(value, list):
        return [mask(item, secrets) for item in value]
    if isinstance(value, dict):
        return {str(key): mask(item, secrets) for key, item in value.items()}
    return value


def cut_input(value: Json) -> Json:
    serialized = json.dumps(value, ensure_ascii=False)
    if len(serialized) <= MAX_TEXT_LENGTH:
        return value
    return {TRUNCATED_INPUT_KEY: serialized[:MAX_TEXT_LENGTH]}


def build_log(lines: List[Dict[str, Json]], secrets: List[str]) -> Dict[str, Json]:
    entries: List[Dict[str, Json]] = []
    actions_by_id: Dict[str, Dict[str, Json]] = {}
    used_at: Dict[str, Optional[datetime]] = {}
    usage_by_message: Dict[str, Dict[str, int]] = {}
    for entry in lines:
        timestamp = entry.get("timestamp")
        message = entry.get("message")
        if entry.get("type") == "assistant" and isinstance(message, dict) and isinstance(message.get("usage"), dict):
            message_id = str(message.get("id") or entry.get("requestId") or len(usage_by_message))
            usage = message["usage"]
            usage_by_message[message_id] = {
                key: int(usage.get(key) or 0)
                for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
            }
        for block in content_blocks(entry):
            block_type = block.get("type")
            if entry.get("type") == "assistant" and block_type == "text":
                text = str(block.get("text", "")).strip()
                if text:
                    entries.append({"kind": "note", "at": timestamp, "text": cut(str(mask(text, secrets)))})
            elif block_type == "tool_use":
                tool_use_id = str(block.get("id", ""))
                action: Dict[str, Json] = {
                    "kind": "action",
                    "at": timestamp,
                    "tool": str(block.get("name", ""))[:200],
                    "input": cut_input(mask(block.get("input"), secrets)),
                }
                actions_by_id[tool_use_id] = action
                used_at[tool_use_id] = parse_time(timestamp)
                entries.append(action)
            elif block_type == "tool_result":
                tool_use_id = str(block.get("tool_use_id", ""))
                action = actions_by_id.get(tool_use_id)
                if action is None:
                    continue
                action["output"] = cut(str(mask(result_text(block), secrets)))
                action["is_error"] = block.get("is_error") is True
                started, finished = used_at.get(tool_use_id), parse_time(timestamp)
                if started is not None and finished is not None:
                    action["duration_ms"] = max(0, int((finished - started).total_seconds() * 1000))
    totals = {key: 0 for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}
    for usage in usage_by_message.values():
        for key in totals:
            totals[key] += usage[key]
    timed_entries = [entry for entry in entries if isinstance(entry.get("at"), str)]
    return {"is_cut": len(timed_entries) > MAX_ENTRIES, "usage": totals, "entries": timed_entries[:MAX_ENTRIES]}


def send_log(url: str, token: str, run_id: str, log: Dict[str, Json]) -> str:
    request = urllib.request.Request(
        f"{url}/api/runs/{run_id}/log",
        data=json.dumps(log).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return str(response.status)
    except urllib.error.HTTPError as error:
        return str(error.code)
    except (OSError, ValueError):
        return "000"


def is_retryable(status: str) -> bool:
    return status == "000" or status.startswith("5")


def save_pending(run_id: str, log: Dict[str, Json]) -> None:
    try:
        PENDING_LOGS_DIRECTORY.mkdir(parents=True, exist_ok=True)
        (PENDING_LOGS_DIRECTORY / f"{run_id}.json").write_text(json.dumps(log), encoding="utf-8")
    except OSError:
        return


def retry_pending(url: str, token: str) -> None:
    if not PENDING_LOGS_DIRECTORY.is_dir():
        return
    for path in sorted(PENDING_LOGS_DIRECTORY.glob("*.json"))[:MAX_PENDING_LOGS]:
        try:
            log = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            path.unlink(missing_ok=True)
            continue
        if not is_retryable(send_log(url, token, path.stem, log)):
            path.unlink(missing_ok=True)


def read_run_id(payload: Dict[str, Json]) -> Optional[str]:
    tool_input = payload.get("tool_input")
    run_id = tool_input.get("run_id") if isinstance(tool_input, dict) else None
    return run_id if isinstance(run_id, str) and run_id else None


def is_error_response(tool_response: Json) -> bool:
    return isinstance(tool_response, dict) and tool_response.get("isError") is True


def main() -> int:
    url = read_setting(URL_VARIABLE_NAMES)
    token = read_setting(TOKEN_VARIABLE_NAMES)
    if url is None or token is None:
        print(MISSING_SETTINGS_MESSAGE, file=sys.stderr)
        return 0
    url = url.rstrip("/")
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    retry_pending(url, token)
    if not isinstance(payload, dict) or is_error_response(payload.get("tool_response")):
        return 0
    run_id = read_run_id(payload)
    transcript_path = payload.get("transcript_path")
    if run_id is None or not isinstance(transcript_path, str):
        return 0
    lines = read_transcript(Path(transcript_path).expanduser())
    found = find_slice(lines, run_id)
    if found is None:
        print(f"Tessio log hook: run {run_id} was not found in the session log.", file=sys.stderr)
        return 0
    start, end = found
    run_lines = lines[start : end + 1]
    log = build_log(run_lines, collect_secrets(run_lines))
    status = send_log(url, token, run_id, log)
    if is_retryable(status):
        save_pending(run_id, log)
    elif not status.startswith("2"):
        print(f"Tessio log hook: Tessio refused the log of run {run_id} ({status}).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
