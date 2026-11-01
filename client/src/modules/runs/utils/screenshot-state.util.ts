import type { RunStatus } from "@/shared/typing/types/test-run.type";
import type { ScreenshotState, StoredFileStatus } from "../typing/types/run.type";

export const resolveScreenshotState = (
  fileId: string | null,
  fileStatus: StoredFileStatus | null,
  runStatus: RunStatus,
): ScreenshotState => {
  if (fileId === null) {
    return "none";
  }

  if (fileStatus === "uploaded") {
    return "uploaded";
  }

  if (fileStatus === "pending" && runStatus === "running") {
    return "uploading";
  }

  return "missing";
};
