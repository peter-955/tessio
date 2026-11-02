import type { ReportReadyPayload } from "../typing/types/notification.type";

export const buildReportSourceHref = (
  projectPath: string,
  source: ReportReadyPayload["source"],
  sourceId: string,
): string => {
  switch (source) {
    case "run":
      return `${projectPath}/runs/${encodeURIComponent(sourceId)}?tab=report`;
    case "plan":
      return `${projectPath}/plans/${encodeURIComponent(sourceId)}`;
    case "story":
      return `${projectPath}/stories/${encodeURIComponent(sourceId)}`;
    default:
      source satisfies never;
      return projectPath;
  }
};
