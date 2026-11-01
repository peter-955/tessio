from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "measure-tokens.sh"
CLAUDE_RESULT = {
    "type": "result",
    "is_error": False,
    "num_turns": 12,
    "duration_ms": 45000,
    "total_cost_usd": 0.42,
    "usage": {
        "input_tokens": 100,
        "cache_creation_input_tokens": 2000,
        "cache_read_input_tokens": 30000,
        "output_tokens": 400,
    },
}
FAKE_CLAUDE = """#!/usr/bin/env bash
printf '%s\\n' "$@" > "$FAKE_CLAUDE_ARGUMENTS"
cat "$FAKE_CLAUDE_RESULT"
"""
BASELINE_INSTRUCTION = "For this measurement take every screenshot at full size."
CSV_HEADER = (
    "timestamp,story,mode,num_turns,input_tokens,cache_creation_input_tokens,cache_read_input_tokens,"
    "output_tokens,total_cost_usd,duration_ms,is_error"
)


@unittest.skipIf(shutil.which("bash") is None, "bash is not installed")
class MeasureTokensTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        binary_directory = root / "bin"
        binary_directory.mkdir()
        fake_claude = binary_directory / "claude"
        fake_claude.write_text(FAKE_CLAUDE)
        fake_claude.chmod(0o755)
        result_file = root / "result.json"
        result_file.write_text(json.dumps(CLAUDE_RESULT))
        self.arguments_file = root / "arguments.txt"
        self.measurements_directory = root / "measurements"
        self.environment = {
            **os.environ,
            "PATH": f"{binary_directory}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_CLAUDE_ARGUMENTS": str(self.arguments_file),
            "FAKE_CLAUDE_RESULT": str(result_file),
            "TESSIO_MEASUREMENTS_DIR": str(self.measurements_directory),
        }

    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT_PATH), *arguments],
            capture_output=True,
            text=True,
            env=self.environment,
            check=False,
        )

    def test_script_is_executable(self) -> None:
        self.assertTrue(os.access(SCRIPT_PATH, os.X_OK))

    def test_scaled_run_saves_the_json_and_appends_a_row(self) -> None:
        completed = self.run_script("SHOP-12", "scaled", "dev")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        arguments = self.arguments_file.read_text().splitlines()
        self.assertEqual(arguments[:2], ["-p", "/tessio:run-story-tests SHOP-12 dev"])
        self.assertIn("--chrome", arguments)
        self.assertIn(str(SCRIPT_PATH.parents[1]), arguments)
        saved_results = list(self.measurements_directory.glob("*-SHOP-12-scaled.json"))
        self.assertEqual(len(saved_results), 1)
        self.assertEqual(json.loads(saved_results[0].read_text()), CLAUDE_RESULT)
        csv_lines = (self.measurements_directory / "measurements.csv").read_text().splitlines()
        self.assertEqual(csv_lines[0], CSV_HEADER)
        expected_values = ["SHOP-12", "scaled", "12", "100", "2000", "30000", "400", "0.42", "45000", "false"]
        self.assertEqual(csv_lines[1].split(",")[1:], expected_values)
        self.assertEqual(completed.stdout.strip(), csv_lines[1])

    def test_baseline_run_asks_for_full_size_screenshots(self) -> None:
        self.assertEqual(self.run_script("SHOP-12", "scaled").returncode, 0)
        self.assertEqual(self.run_script("SHOP-12", "baseline").returncode, 0)
        prompt = self.arguments_file.read_text().splitlines()[1]
        self.assertEqual(prompt, f"/tessio:run-story-tests SHOP-12 {BASELINE_INSTRUCTION}")
        csv_lines = (self.measurements_directory / "measurements.csv").read_text().splitlines()
        self.assertEqual(len(csv_lines), 3)
        self.assertEqual(csv_lines.count(CSV_HEADER), 1)

    def test_unknown_mode_is_refused(self) -> None:
        completed = self.run_script("SHOP-12", "other")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("Usage:", completed.stderr)


if __name__ == "__main__":
    unittest.main()
