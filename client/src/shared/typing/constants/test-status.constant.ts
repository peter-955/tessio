import type { DSBadgeColor } from "@/components/design-system";
import type { RunStatus, TestOutcome } from "../types/test-run.type";

export const TEST_STATUS_COLORS: Record<TestOutcome, DSBadgeColor> = {
  running: "tessio",
  passed: "green",
  failed: "red",
  aborted: "yellow",
  blocked: "yellow",
  skipped: "gray",
  pending: "gray",
  not_reported: "gray",
};

export const RUN_STATUSES: RunStatus[] = ["running", "passed", "failed", "aborted"];
