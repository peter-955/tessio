import type { TestCasePriority } from "./test-case.type";

export type DiffTokenKind = "added" | "removed" | "unchanged";

export interface DiffToken {
  value: string;
  kind: DiffTokenKind;
}

export interface TextDiffLabels {
  added: string;
  removed: string;
}

export type TextDiffField = "title" | "businessValue" | "preconditions";

export type StepChangeKind = "added" | "removed" | "changed";

export interface StepDiff {
  position: number;
  change: StepChangeKind;
  action: DiffToken[];
  expected: DiffToken[];
}

export type VersionDiffEntry =
  | { field: TextDiffField; kind: "text"; tokens: DiffToken[] }
  | { field: "priority"; kind: "priority"; from: TestCasePriority; to: TestCasePriority }
  | { field: "steps"; kind: "steps"; steps: StepDiff[] }
  | { field: "criteria"; kind: "criteria"; tokens: DiffToken[] }
  | { field: "files"; kind: "files"; added: number; removed: number };
