import {
  CHROME_TOOL_PREFIXES,
  MAX_LABEL_VALUE_LENGTH,
  TESSIO_TOOL_PREFIX,
} from "../typing/constants/run-log.constant";
import type { RunLog, RunLogEntry, RunLogLabel, RunLogSection } from "../typing/types/run-log.type";

const shorten = (value: unknown): string => {
  const text = typeof value === "string" ? value : JSON.stringify(value ?? "");
  return text.length > MAX_LABEL_VALUE_LENGTH ? `${text.slice(0, MAX_LABEL_VALUE_LENGTH)}…` : text;
};

const isRecord = (value: unknown): value is Record<string, unknown> => {
  return typeof value === "object" && value !== null && !Array.isArray(value);
};

const readInput = (entry: RunLogEntry): Record<string, unknown> => {
  return isRecord(entry.input) ? entry.input : {};
};

const buildChromeLabel = (name: string, input: Record<string, unknown>): RunLogLabel => {
  if (name === "navigate") {
    return { key: "log.labels.opened", values: { url: shorten(input.url) } };
  }
  if (name === "form_input") {
    return { key: "log.labels.filled", values: { value: shorten(input.value) } };
  }
  if (name === "find") {
    return { key: "log.labels.lookedFor", values: { query: shorten(input.query) } };
  }
  if (name === "read_page" || name === "get_page_text") {
    return { key: "log.labels.readPage", values: {} };
  }
  if (name === "file_upload") {
    return { key: "log.labels.attachedFile", values: {} };
  }
  if (name === "computer") {
    const action = typeof input.action === "string" ? input.action : "";
    if (action === "screenshot") {
      return { key: "log.labels.screenshot", values: {} };
    }
    if (action === "type") {
      return { key: "log.labels.typed", values: { text: shorten(input.text) } };
    }
    if (action === "key") {
      return { key: "log.labels.pressed", values: { key: shorten(input.text) } };
    }
    if (action === "scroll") {
      return { key: "log.labels.scrolled", values: {} };
    }
    if (action.includes("click")) {
      return { key: "log.labels.clicked", values: {} };
    }
  }

  return { key: "log.labels.tool", values: { tool: name } };
};

export const buildRunLogLabel = (entry: RunLogEntry): RunLogLabel => {
  const tool = entry.tool ?? "";
  const input = readInput(entry);
  const chromePrefix = CHROME_TOOL_PREFIXES.find((prefix) => {
    return tool.startsWith(prefix);
  });
  if (chromePrefix !== undefined) {
    return buildChromeLabel(tool.slice(chromePrefix.length), input);
  }
  if (tool.startsWith(TESSIO_TOOL_PREFIX)) {
    return { key: "log.labels.tessio", values: { tool: tool.slice(TESSIO_TOOL_PREFIX.length) } };
  }
  if (tool === "Bash") {
    return { key: "log.labels.ran", values: { command: shorten(input.command) } };
  }

  return { key: "log.labels.tool", values: { tool } };
};

export const groupRunLogEntries = (entries: readonly RunLogEntry[]): RunLogSection[] => {
  const sections: RunLogSection[] = [];
  entries.forEach((entry) => {
    const last = sections[sections.length - 1];
    if (last !== undefined && last.phase === entry.phase && last.testCaseId === entry.testCaseId) {
      last.entries.push(entry);
      return;
    }
    sections.push({
      id: `${entry.phase}-${entry.testCaseId ?? "none"}-${entry.position}`,
      phase: entry.phase,
      testCaseId: entry.testCaseId,
      entries: [entry],
    });
  });

  return sections;
};

export const formatElapsed = (startAt: string, at: string): string => {
  const seconds = Math.max(0, Math.round((Date.parse(at) - Date.parse(startAt)) / 1000));
  const minutes = Math.floor(seconds / 60);

  return `+${minutes}:${String(seconds % 60).padStart(2, "0")}`;
};

export const sumTokens = (usage: NonNullable<RunLog["usage"]>): number => {
  return (
    usage.inputTokens +
    usage.cacheCreationInputTokens +
    usage.cacheReadInputTokens +
    usage.outputTokens
  );
};
