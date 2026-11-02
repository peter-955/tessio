---
name: import-cases
description: Import test cases into Tessio from any file (xlsx, csv, docx, pdf, text or an image of a sheet) as Draft cases for QC to review. Use when asked to import, upload, convert or move test cases or a test plan file into Tessio.
argument-hint: <file> [STORY-KEY]
allowed-tools: mcp__plugin_tessio_tessio__*, Read, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract_file.py *)
---

# Import test cases from a file

Arguments: `$ARGUMENTS` = `<file> [STORY-KEY]`.

1. **Read the file.**
   - `.xlsx` or `.docx`: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract_file.py <file>`. It prints each sheet as `row <n>: cell | cell | ...`. `⏎` is a line break inside a cell, and `\|` is a `|` inside a cell.
   - `.csv`, `.txt`, `.md`, `.pdf`, `.png`, `.jpg`: read it directly.
   - Any other format, or a file that cannot be read: say so and stop.
2. **Find the story of each case**, in this order: the `STORY-KEY` argument, a Story or Jira key column, the sheet tab name, a heading that holds a Jira key. A case with no story is listed in the summary as "no story" and is not sent.
3. **Load each story:** call `get_story_context(story_key)` once per story. Note its AC codes and its data keys.
4. **Build the cases** with the mapping rules in [references/create-cases.md](references/create-cases.md). Give each case a `source` that points back at the file: `Sheet SHOP-12, rows 4-9`, `page 3`, `table 2, row 5`.
5. Follow [references/create-cases.md](references/create-cases.md) from "Check" to the end.
