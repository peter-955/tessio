import type { AiHarness } from "../../typing/types/ai-harness.type";

export const createAiHarness = (changes: Partial<AiHarness> = {}): AiHarness => {
  return {
    server: { version: "0.1.0", buildCommit: "6792d1a" },
    plugin: {
      name: "tessio",
      version: "0.3.0",
      description: "Run Tessio test cases with Claude",
      updateCommand:
        "claude plugin marketplace update tessio && claude plugin update tessio@tessio",
    },
    skills: [
      {
        name: "run-story-tests",
        command: "/tessio:run-story-tests",
        argumentHint: "<STORY-KEY> [environment] [case codes]",
        description: "Run the Ready Tessio test cases of a Jira story.",
      },
    ],
    commands: [],
    hooks: [
      {
        event: "PostToolUse",
        toolName: "record_case_result",
        script: "hooks/upload_screenshots.py",
        timeoutSeconds: 120,
      },
    ],
    mcpServers: [
      {
        name: "tessio",
        transport: "http",
        url: "https://tessio.test/mcp",
        headerNames: ["Authorization", "X-Tessio-Plugin-Version"],
      },
    ],
    mcpTools: [
      {
        name: "start_run",
        description: "Start a test run for a story.",
        capability: "run.start",
        roles: ["admin", "qc", "dev"],
      },
    ],
    ...changes,
  };
};
