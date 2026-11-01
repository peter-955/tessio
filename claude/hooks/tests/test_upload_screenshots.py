from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import upload_screenshots

CASE_RESULT_TEXT = json.dumps({"case_result_id": "C"})
SIGNED_UPLOAD_PATH = "/api/runs/R/case-results/C/screenshot-upload"


class RecordingServer(ThreadingHTTPServer):
    bucket_status: int
    bucket_bodies: list[bytes]
    authorization_headers: list[str]


class RecordingHandler(BaseHTTPRequestHandler):
    server: RecordingServer

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(content_length) if content_length else b""
        if self.path == SIGNED_UPLOAD_PATH:
            self.server.authorization_headers.append(self.headers.get("Authorization") or "")
            port = self.server.server_address[1]
            response = {"url": f"http://127.0.0.1:{port}/bucket", "keyPrefix": "p/", "fields": {"policy": "x"}}
            encoded = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        if self.path == "/bucket":
            self.server.bucket_bodies.append(body)
            self.send_response(self.server.bucket_status)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, message_format: str, *arguments: object) -> None:
        return


def build_payload(steps: list[object]) -> str:
    return json.dumps(
        {
            "tool_name": "mcp__plugin_tessio_tessio__record_case_result",
            "tool_input": {"run_id": "R", "case_id": "K", "status": "passed", "duration_ms": 10, "steps": steps},
            "tool_response": [{"type": "text", "text": CASE_RESULT_TEXT}],
        }
    )


class PendingFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.pending_file = Path(self.temporary_directory.name) / "pending-uploads.jsonl"
        pending_patch = mock.patch.object(upload_screenshots, "PENDING_UPLOADS_FILE", self.pending_file)
        pending_patch.start()
        self.addCleanup(pending_patch.stop)

    def run_main(self, stdin_text: str, environment: dict[str, str]) -> tuple[int, str]:
        stderr = io.StringIO()
        full_environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), **environment}
        environment_patch = mock.patch.dict(os.environ, full_environment, clear=True)
        stdin_patch = mock.patch.object(sys, "stdin", io.StringIO(stdin_text))
        stderr_patch = mock.patch.object(sys, "stderr", stderr)
        with environment_patch, stdin_patch, stderr_patch:
            exit_code = upload_screenshots.main()
        return exit_code, stderr.getvalue()

    def read_pending_lines(self) -> list[str]:
        if not self.pending_file.is_file():
            return []
        return [line for line in self.pending_file.read_text().splitlines() if line.strip()]


class ReadCaseResultIdTest(unittest.TestCase):
    def test_list_of_text_blocks_gives_the_id(self) -> None:
        tool_response = [{"type": "text", "text": CASE_RESULT_TEXT}]
        self.assertEqual(upload_screenshots.read_case_result_id(tool_response), "C")

    def test_string_gives_the_id(self) -> None:
        self.assertEqual(upload_screenshots.read_case_result_id(CASE_RESULT_TEXT), "C")

    def test_dict_with_content_gives_the_id(self) -> None:
        tool_response = {"content": [{"type": "text", "text": CASE_RESULT_TEXT}]}
        self.assertEqual(upload_screenshots.read_case_result_id(tool_response), "C")

    def test_plain_text_gives_none(self) -> None:
        tool_response = [{"type": "text", "text": "Sign in to continue."}]
        self.assertIsNone(upload_screenshots.read_case_result_id(tool_response))

    def test_error_result_gives_none(self) -> None:
        tool_response = {"isError": True, "content": [{"type": "text", "text": CASE_RESULT_TEXT}]}
        self.assertIsNone(upload_screenshots.read_case_result_id(tool_response))

    def test_json_without_the_key_gives_none(self) -> None:
        tool_response = [{"type": "text", "text": json.dumps({"other": "value"})}]
        self.assertIsNone(upload_screenshots.read_case_result_id(tool_response))

    def test_non_text_block_gives_none(self) -> None:
        tool_response = [{"type": "image", "data": "abc"}]
        self.assertIsNone(upload_screenshots.read_case_result_id(tool_response))

    def test_json_list_gives_none(self) -> None:
        self.assertIsNone(upload_screenshots.read_case_result_id("[1, 2]"))

    def test_none_gives_none(self) -> None:
        self.assertIsNone(upload_screenshots.read_case_result_id(None))


class BuildUploadsTest(unittest.TestCase):
    def test_keeps_only_steps_with_a_screenshot(self) -> None:
        payload = json.loads(
            build_payload(
                [
                    {"order": 1, "status": "passed", "screenshot_path": "/screenshots/one.jpg"},
                    {"order": 2, "status": "passed"},
                    {"status": "passed", "screenshot_path": "/screenshots/no-order.jpg"},
                    "not a step",
                ]
            )
        )
        self.assertEqual(
            upload_screenshots.build_uploads(payload),
            [{"path": "/screenshots/one.jpg", "order": 1, "run_id": "R", "case_result_id": "C"}],
        )

    def test_missing_run_id_gives_no_uploads(self) -> None:
        payload = json.loads(build_payload([{"order": 1, "screenshot_path": "/screenshots/one.jpg"}]))
        del payload["tool_input"]["run_id"]
        self.assertEqual(upload_screenshots.build_uploads(payload), [])

    def test_non_dict_tool_input_gives_no_uploads(self) -> None:
        self.assertEqual(upload_screenshots.build_uploads({"tool_input": "text"}), [])
        self.assertEqual(upload_screenshots.build_uploads(["not", "a", "payload"]), [])


class ResolveSettingsTest(unittest.TestCase):
    def test_plugin_options_win(self) -> None:
        environment = {
            "CLAUDE_PLUGIN_OPTION_TESSIO_URL": "https://plugin.example.com",
            "CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN": "plugin-token",
            "TESSIO_URL": "https://manual.example.com",
            "TESSIO_TOKEN": "manual-token",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            self.assertEqual(upload_screenshots.resolve_settings(), ("https://plugin.example.com", "plugin-token"))

    def test_falls_back_to_manual_variables(self) -> None:
        environment = {
            "CLAUDE_PLUGIN_OPTION_TESSIO_URL": "",
            "TESSIO_URL": "https://manual.example.com",
            "TESSIO_TOKEN": "manual-token",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            self.assertEqual(upload_screenshots.resolve_settings(), ("https://manual.example.com", "manual-token"))

    def test_missing_value_gives_none(self) -> None:
        with mock.patch.dict(os.environ, {"TESSIO_URL": "https://manual.example.com"}, clear=True):
            self.assertIsNone(upload_screenshots.resolve_settings())
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(upload_screenshots.resolve_settings())

    def test_trailing_slash_is_stripped(self) -> None:
        environment = {"TESSIO_URL": "https://manual.example.com/", "TESSIO_TOKEN": "manual-token"}
        with mock.patch.dict(os.environ, environment, clear=True):
            self.assertEqual(upload_screenshots.resolve_settings(), ("https://manual.example.com", "manual-token"))


class MainGuardTest(PendingFileTestCase):
    def test_invalid_stdin_exits_cleanly(self) -> None:
        environment = {"TESSIO_URL": "http://127.0.0.1:9", "TESSIO_TOKEN": "tok"}
        exit_code, stderr = self.run_main("not json", environment)
        self.assertEqual(exit_code, 0)
        self.assertNotIn("Traceback", stderr)

    def test_missing_settings_prints_the_message(self) -> None:
        exit_code, stderr = self.run_main(build_payload([]), {})
        self.assertEqual(exit_code, 0)
        self.assertIn("CLAUDE_PLUGIN_OPTION_TESSIO_URL", stderr)
        self.assertIn("TESSIO_TOKEN", stderr)

    def test_error_result_uploads_nothing(self) -> None:
        payload = json.loads(build_payload([{"order": 1, "screenshot_path": "/screenshots/one.jpg"}]))
        payload["tool_response"] = {"isError": True, "content": [{"type": "text", "text": "Run not found."}]}
        environment = {"TESSIO_URL": "http://127.0.0.1:9", "TESSIO_TOKEN": "tok"}
        exit_code, stderr = self.run_main(json.dumps(payload), environment)
        self.assertEqual(exit_code, 0)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(self.read_pending_lines(), [])

    def test_invalid_pending_lines_are_skipped(self) -> None:
        self.pending_file.write_text('not json\n{"path": "/x.jpg"}\n')
        self.assertEqual(upload_screenshots.read_pending_uploads(), [])

    def test_a_line_that_is_not_utf8_is_skipped_and_valid_lines_are_kept(self) -> None:
        valid_upload = {"path": "/x.jpg", "order": 1, "run_id": "run", "case_result_id": "case"}
        self.pending_file.write_bytes(json.dumps(valid_upload).encode() + b"\n\xff garbage\n")
        self.assertEqual(upload_screenshots.read_pending_uploads(), [valid_upload])


@unittest.skipIf(shutil.which("curl") is None, "curl is not installed")
class UploadEndToEndTest(PendingFileTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.server = RecordingServer(("127.0.0.1", 0), RecordingHandler)
        self.server.bucket_status = 204
        self.server.bucket_bodies = []
        self.server.authorization_headers = []
        server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        server_thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.screenshot = Path(self.temporary_directory.name) / "step.jpg"
        self.screenshot.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg")
        self.environment = {
            "CLAUDE_PLUGIN_OPTION_TESSIO_URL": f"http://127.0.0.1:{self.server.server_address[1]}/",
            "CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN": "tok",
        }

    def test_uploads_the_screenshot_with_the_signed_key(self) -> None:
        payload = build_payload([{"order": 3, "status": "passed", "screenshot_path": str(self.screenshot)}])
        exit_code, stderr = self.run_main(payload, self.environment)
        self.assertEqual(exit_code, 0)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(self.server.authorization_headers, ["Bearer tok"])
        self.assertEqual(len(self.server.bucket_bodies), 1)
        body = self.server.bucket_bodies[0]
        self.assertIn(b'name="key"', body)
        self.assertIn(b"p/3.jpg", body)
        self.assertIn(b"fake-jpeg", body)
        self.assertIn(b'name="policy"', body)
        self.assertEqual(self.read_pending_lines(), [])

    def test_failed_upload_is_retried_on_the_next_run(self) -> None:
        self.server.bucket_status = 500
        payload = build_payload([{"order": 3, "status": "passed", "screenshot_path": str(self.screenshot)}])
        self.run_main(payload, self.environment)
        pending_lines = self.read_pending_lines()
        self.assertEqual(len(pending_lines), 1)
        self.assertEqual(json.loads(pending_lines[0])["order"], 3)
        self.server.bucket_status = 204
        exit_code, stderr = self.run_main(build_payload([]), self.environment)
        self.assertEqual(exit_code, 0)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(len(self.server.bucket_bodies), 2)
        self.assertIn(b"p/3.jpg", self.server.bucket_bodies[1])
        self.assertEqual(self.read_pending_lines(), [])


if __name__ == "__main__":
    unittest.main()
