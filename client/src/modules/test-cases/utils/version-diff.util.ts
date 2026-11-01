import { diffArrays, diffWords, type ChangeObject } from "diff";
import type { LinkedCriterion, TestCaseVersion, TestStep } from "../typing/types/test-case.type";
import type {
  DiffToken,
  StepChangeKind,
  StepDiff,
  TextDiffField,
  VersionDiffEntry,
} from "../typing/types/version-diff.type";

type CriterionReference = Pick<LinkedCriterion, "id" | "code">;

const TEXT_FIELDS: TextDiffField[] = ["title", "businessValue", "preconditions"];

const toTokenKind = (change: ChangeObject<unknown>): DiffToken["kind"] => {
  if (change.added) {
    return "added";
  }

  return change.removed ? "removed" : "unchanged";
};

export const buildWordDiff = (older: string, newer: string): DiffToken[] => {
  return diffWords(older, newer).map((change) => {
    return { value: change.value, kind: toTokenKind(change) };
  });
};

const sortSteps = (steps: readonly TestStep[]): TestStep[] => {
  return [...steps].sort((first, second) => first.order - second.order);
};

const resolveStepChange = (
  olderStep: TestStep | undefined,
  newerStep: TestStep | undefined,
): StepChangeKind => {
  if (olderStep === undefined) {
    return "added";
  }

  return newerStep === undefined ? "removed" : "changed";
};

const buildStepDiff = (
  position: number,
  olderStep: TestStep | undefined,
  newerStep: TestStep | undefined,
): StepDiff | null => {
  const olderAction = olderStep?.action ?? "";
  const newerAction = newerStep?.action ?? "";
  const olderExpected = olderStep?.expected ?? "";
  const newerExpected = newerStep?.expected ?? "";

  if (olderStep !== undefined && newerStep !== undefined) {
    if (olderAction === newerAction && olderExpected === newerExpected) {
      return null;
    }
  }

  return {
    position,
    change: resolveStepChange(olderStep, newerStep),
    action: buildWordDiff(olderAction, newerAction),
    expected: buildWordDiff(olderExpected, newerExpected),
  };
};

const buildStepDiffs = (older: TestCaseVersion, newer: TestCaseVersion): StepDiff[] => {
  const olderSteps = sortSteps(older.steps);
  const newerSteps = sortSteps(newer.steps);
  const stepCount = Math.max(olderSteps.length, newerSteps.length);
  const stepDiffs: StepDiff[] = [];

  for (let index = 0; index < stepCount; index += 1) {
    const stepDiff = buildStepDiff(index + 1, olderSteps[index], newerSteps[index]);
    if (stepDiff !== null) {
      stepDiffs.push(stepDiff);
    }
  }

  return stepDiffs;
};

const buildCriterionTokens = (
  older: TestCaseVersion,
  newer: TestCaseVersion,
  criteria: readonly CriterionReference[],
): DiffToken[] => {
  const codes = new Map(criteria.map((criterion) => [criterion.id, criterion.code]));
  const readCode = (id: string): string => codes.get(id) ?? id;
  const sortIds = (ids: readonly string[]): string[] => {
    return [...ids].sort((first, second) => readCode(first).localeCompare(readCode(second)));
  };

  return diffArrays(sortIds(older.criterionIds), sortIds(newer.criterionIds)).flatMap((change) => {
    return change.value.map((id): DiffToken => {
      return { value: readCode(id), kind: toTokenKind(change) };
    });
  });
};

export const buildVersionDiff = (
  older: TestCaseVersion,
  newer: TestCaseVersion,
  criteria: readonly CriterionReference[],
): VersionDiffEntry[] => {
  const entries: VersionDiffEntry[] = [];

  for (const field of TEXT_FIELDS) {
    const olderText = older[field] ?? "";
    const newerText = newer[field] ?? "";
    if (olderText !== newerText) {
      entries.push({ field, kind: "text", tokens: buildWordDiff(olderText, newerText) });
    }
  }

  if (older.priority !== newer.priority) {
    entries.push({ field: "priority", kind: "priority", from: older.priority, to: newer.priority });
  }

  const steps = buildStepDiffs(older, newer);
  if (steps.length > 0) {
    entries.push({ field: "steps", kind: "steps", steps });
  }

  const criterionTokens = buildCriterionTokens(older, newer, criteria);
  if (criterionTokens.some((token) => token.kind !== "unchanged")) {
    entries.push({ field: "criteria", kind: "criteria", tokens: criterionTokens });
  }

  const olderFiles = new Set(older.fileVersionIds);
  const newerFiles = new Set(newer.fileVersionIds);
  const addedFileCount = newer.fileVersionIds.filter((id) => !olderFiles.has(id)).length;
  const removedFileCount = older.fileVersionIds.filter((id) => !newerFiles.has(id)).length;
  if (addedFileCount > 0 || removedFileCount > 0) {
    entries.push({
      field: "files",
      kind: "files",
      added: addedFileCount,
      removed: removedFileCount,
    });
  }

  return entries;
};
