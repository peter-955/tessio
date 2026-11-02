import type { FlakyCaseBadgeDefinition } from "../types/flaky-case-badge.type";

export const MAX_QUARANTINE_REASON_LENGTH = 500;

export const FLAKY_CASE_BADGES: readonly FlakyCaseBadgeDefinition[] = [
  { kind: "flaky", flag: "isFlaky", icon: "flaky", color: "yellow" },
  { kind: "disagreeing", flag: "isDisagreeing", icon: "alert", color: "red" },
  { kind: "quarantined", flag: "isQuarantined", icon: "quarantine", color: "gray" },
];
