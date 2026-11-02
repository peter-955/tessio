from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import upload_run_log

RUN_ID = "run-1"
SECRET = "hunter2-very-secret"
TESSIO = "mcp__plugin_tessio_tessio__"


def assistant(timestamp: str, blocks: List[Dict[str, object]], message_id: str = "", output_tokens: int = 0) -> Dict[str, object]:
    message: Dict[str, object] = {"content": blocks}
    if message_id:
        message["id"] = message_id
        message["usage"] = {"input_tokens": 1, "cache_read_input_tokens": 100, "output_tokens": output_tokens}
    return {"type": "assistant", "timestamp": timestamp, "message": message}


def result(timestamp: str, tool_use_id: str, content: object, is_error: bool = False) -> Dict[str, object]:
    block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content, "is_error": is_error}
    return {"type": "user", "timestamp": timestamp, "message": {"content": [block]}}


def tool(tool_use_id: str, name: str, tool_input: Dict[str, object]) -> Dict[str, object]:
    return {"type": "tool_use", "id": tool_use_id, "name": name, "input": tool_input}


TRANSCRIPT: List[Dict[str, object]] = [
    {"type": "user", "timestamp": "2026-11-01T08:59:00Z", "message": {"content": "Run SHOP-1"}},
    assistant("2026-11-01T08:59:30Z", [{"type": "text", "text": "Before the run"}]),
    assistant("2026-11-01T09:00:00Z", [tool("t1", f"{TESSIO}start_run", {"story_key": "SHOP-1"})], "m1", 10),
    result("2026-11-01T09:00:01Z", "t1", [{"type": "text", "text": json.dumps({"run_id": RUN_ID})}]),
    assistant("2026-11-01T09:00:02Z", [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "Signing in."}], "m2", 5),
    assistant("2026-11-01T09:00:03Z", [tool("t2", f"{TESSIO}resolve_data", {"run_id": RUN_ID, "keys": ["pw"]})], "m2", 5),
    result("2026-11-01T09:00:04Z", "t2", json.dumps({"values": {"pw": SECRET}})),
    assistant("2026-11-01T09:00:05Z", [tool("t3", "mcp__claude-in-chrome__computer", {"action": "type", "text": SECRET})], "m3", 7),
    result("2026-11-01T09:00:06.500Z", "t3", [{"type": "image", "source": {}}, {"type": "text", "text": f"Typed {SECRET}\x00"}]),
    {"type": "assistant", "isSidechain": True, "timestamp": "2026-11-01T09:00:07Z", "message": {"content": [{"type": "text", "text": "Subagent"}]}},
    assistant("2026-11-01T09:00:08Z", [tool("t4", f"{TESSIO}record_case_result", {"run_id": RUN_ID, "case_id": "c1", "notes": "x" * 5000})]),
    result("2026-11-01T09:00:09Z", "t4", "denied", is_error=True),
    assistant("2026-11-01T09:00:10Z", [tool("t5", f"{TESSIO}finish_run", {"run_id": RUN_ID})]),
    assistant("2026-11-01T09:00:11Z", [{"type": "text", "text": "After the run"}]),
]


class RecordingServer(ThreadingHTTPServer):
    status: int
    bodies: List[Dict[str, object]]
    authorizations: List[str]


class RecordingHandler(BaseHTTPRequestHandler):
    server: RecordingServer

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        self.server.bodies.append(json.loads(self.rfile.read(length)))
        self.server.authorizations.append(self.headers.get("Authorization") or "")
        self.send_response(self.server.status if self.path.endswith("/log") else 404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, message_format: str, *arguments: object) -> None:
        return


class UploadRunLogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.pending = self.folder / "pending"
        patcher = mock.patch.object(upload_run_log, "PENDING_LOGS_DIRECTORY", self.pending)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.transcript = self.folder / "session.jsonl"
        self.transcript.write_text("".join(json.dumps(line) + "\n" for line in TRANSCRIPT) + "not json\n")
        self.server = RecordingServer(("127.0.0.1", 0), RecordingHandler)
        self.server.status = 201
        self.server.bodies = []
        self.server.authorizations = []
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def run_hook(self, payload: Dict[str, object], environment: Dict[str, str] | None = None) -> tuple[int, str]:
        settings = {"CLAUDE_PLUGIN_OPTION_TESSIO_URL": self.url, "CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN": "tsio_x"}
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, settings if environment is None else environment, clear=True):
            with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), mock.patch.object(sys, "stderr", stderr):
                code = upload_run_log.main()
        return code, stderr.getvalue()

    def payload(self) -> Dict[str, object]:
        return {
            "tool_name": f"{TESSIO}finish_run",
            "tool_input": {"run_id": RUN_ID},
            "tool_response": [{"type": "text", "text": "{}"}],
            "transcript_path": str(self.transcript),
        }

    def test_the_run_slice_is_uploaded_with_secrets_masked_and_images_dropped(self) -> None:
        code, stderr = self.run_hook(self.payload())

        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(self.server.authorizations, ["Bearer tsio_x"])
        [log] = self.server.bodies
        entries = log["entries"]
        assert isinstance(entries, list)
        self.assertEqual(
            [(entry["kind"], entry.get("tool", entry.get("text"))) for entry in entries],
            [
                ("action", f"{TESSIO}start_run"),
                ("note", "Signing in."),
                ("action", f"{TESSIO}resolve_data"),
                ("action", "mcp__claude-in-chrome__computer"),
                ("action", f"{TESSIO}record_case_result"),
                ("action", f"{TESSIO}finish_run"),
            ],
        )
        typed = entries[3]
        self.assertEqual(typed["input"], {"action": "type", "text": "••••"})
        self.assertEqual(typed["output"], "[screenshot]\nTyped ••••")
        self.assertEqual(typed["duration_ms"], 1500)
        self.assertEqual(entries[2]["output"], json.dumps({"values": {"pw": "••••"}}, ensure_ascii=False))
        self.assertEqual(set(entries[4]["input"]), {"truncated"})
        self.assertTrue(entries[4]["is_error"])
        self.assertNotIn(SECRET, json.dumps(log))
        self.assertEqual(
            log["usage"],
            {"input_tokens": 3, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 300, "output_tokens": 22},
        )
        self.assertIs(log["is_cut"], False)

    def test_a_failed_upload_waits_and_is_retried_on_the_next_run(self) -> None:
        self.server.status = 503
        self.run_hook(self.payload())
        self.assertEqual([path.name for path in self.pending.iterdir()], [f"{RUN_ID}.json"])

        self.server.status = 201
        other = dict(self.payload(), tool_input={"run_id": "unknown-run"})
        _, stderr = self.run_hook(other)

        self.assertEqual(list(self.pending.iterdir()), [])
        self.assertEqual(len(self.server.bodies), 2)
        self.assertIn("unknown-run was not found", stderr)

    def test_a_refused_log_is_reported_and_not_kept(self) -> None:
        self.server.status = 409

        _, stderr = self.run_hook(self.payload())

        self.assertIn("refused the log of run run-1 (409)", stderr)
        self.assertFalse(self.pending.exists())

    def test_nothing_is_sent_without_settings_or_after_a_failed_finish(self) -> None:
        missing_code, missing_stderr = self.run_hook(self.payload(), environment={})
        failed = dict(self.payload(), tool_response={"isError": True})
        failed_code, _ = self.run_hook(failed)

        self.assertEqual((missing_code, failed_code), (0, 0))
        self.assertIn("tessio_url and tessio_token", missing_stderr)
        self.assertEqual(self.server.bodies, [])

    def test_a_long_run_is_cut(self) -> None:
        with mock.patch.object(upload_run_log, "MAX_ENTRIES", 2):
            self.run_hook(self.payload())

        [log] = self.server.bodies
        self.assertIs(log["is_cut"], True)
        self.assertEqual(len(log["entries"]), 2)


if __name__ == "__main__":
    unittest.main()
