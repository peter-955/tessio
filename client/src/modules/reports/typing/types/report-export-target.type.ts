export type ReportExportTarget =
  | { source: "run"; runId: string }
  | { source: "plan"; planId: string }
  | { source: "story"; jiraKey: string };
