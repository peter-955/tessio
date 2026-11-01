import type { RunCounts } from "@/shared/typing/types/test-run.type";
import { RUN_COUNT_KEYS } from "../typing/constants/run.constant";
import type { RunCountEntry } from "../typing/types/run.type";

export const listCountEntries = (counts: RunCounts): RunCountEntry[] => {
  return RUN_COUNT_KEYS.map((key): RunCountEntry => {
    return { key, count: counts[key] };
  }).filter((entry) => {
    return entry.count > 0;
  });
};

export const countReportedCases = (counts: RunCounts): number => {
  return counts.passed + counts.failed + counts.blocked + counts.skipped;
};
