#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") <STORY-KEY> <baseline|scaled> [environment]" >&2
  exit 2
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage
fi

story_key="$1"
mode="$2"
environment="${3:-}"

case "$mode" in
  baseline | scaled) ;;
  *) usage ;;
esac

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(dirname "$script_directory")"
measurements_directory="${TESSIO_MEASUREMENTS_DIR:-$HOME/.tessio/measurements}"
allowed_tools="mcp__plugin_tessio_tessio__*,mcp__claude-in-chrome__*,Bash(curl:*),Bash(mkdir:*)"

prompt="/tessio:run-story-tests $story_key"
if [[ -n "$environment" ]]; then
  prompt="$prompt $environment"
fi
if [[ "$mode" == "baseline" ]]; then
  prompt="$prompt For this measurement take every screenshot at full size."
fi

mkdir -p "$measurements_directory"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
result_file="$measurements_directory/$timestamp-$story_key-$mode.json"
csv_file="$measurements_directory/measurements.csv"

claude_status=0
claude -p "$prompt" \
  --plugin-dir "$plugin_root" \
  --chrome \
  --output-format json \
  --allowedTools "$allowed_tools" >"$result_file" || claude_status=$?

if [[ ! -f "$csv_file" ]]; then
  echo "timestamp,story,mode,num_turns,input_tokens,cache_creation_input_tokens,cache_read_input_tokens,output_tokens,total_cost_usd,duration_ms,is_error" >"$csv_file"
fi

row="$(python3 -c '
import json
import sys

timestamp, story_key, mode, result_path, claude_status = sys.argv[1:6]
try:
    with open(result_path) as result_file:
        result = json.load(result_file)
except ValueError:
    result = {}
if not isinstance(result, dict):
    result = {}
usage = result.get("usage")
if not isinstance(usage, dict):
    usage = {}
is_error = bool(result.get("is_error", True)) or claude_status != "0"
values = [
    timestamp,
    story_key,
    mode,
    result.get("num_turns", ""),
    usage.get("input_tokens", ""),
    usage.get("cache_creation_input_tokens", ""),
    usage.get("cache_read_input_tokens", ""),
    usage.get("output_tokens", ""),
    result.get("total_cost_usd", ""),
    result.get("duration_ms", ""),
    str(is_error).lower(),
]
print(",".join(str(value) for value in values))
' "$timestamp" "$story_key" "$mode" "$result_file" "$claude_status")"

echo "$row" >>"$csv_file"
echo "$row"
echo "Saved $result_file and appended to $csv_file" >&2
