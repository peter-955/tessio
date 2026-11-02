import {
  checkIsSameDataTable,
  formatDataTableText,
} from "@/modules/data-rows/utils/data-table-text.util";
import type { TestCaseVersion, TestStep } from "@/modules/test-cases/typing/types/test-case.type";
import type { DiffToken } from "@/modules/test-cases/typing/types/version-diff.type";
import { buildWordDiff } from "@/modules/test-cases/utils/version-diff.util";
import { diffArrays } from "diff";
import type {
  CompareDataTableRow,
  ComparePriorityRow,
  CompareStepRow,
  CompareStepSide,
  CompareTextField,
  CompareTextRow,
  VersionComparison,
} from "../typing/types/version-comparison.type";

const TEXT_FIELDS: CompareTextField[] = ["title", "businessValue", "preconditions"];

const keepOlderTokens = (tokens: readonly DiffToken[]): DiffToken[] => {
  return tokens.filter((token) => token.kind !== "added");
};

const keepNewerTokens = (tokens: readonly DiffToken[]): DiffToken[] => {
  return tokens.filter((token) => token.kind !== "removed");
};

const toTokens = (text: string, kind: DiffToken["kind"]): DiffToken[] => {
  return text === "" ? [] : [{ value: text, kind }];
};

const buildTextRow = (field: CompareTextField, older: string, newer: string): CompareTextRow => {
  if (older === newer) {
    return {
      field,
      kind: "unchanged",
      left: toTokens(older, "unchanged"),
      right: toTokens(newer, "unchanged"),
    };
  }

  const tokens = buildWordDiff(older, newer);

  return { field, kind: "changed", left: keepOlderTokens(tokens), right: keepNewerTokens(tokens) };
};

const buildPriorityRow = (older: TestCaseVersion, newer: TestCaseVersion): ComparePriorityRow => {
  return {
    kind: older.priority === newer.priority ? "unchanged" : "changed",
    left: older.priority,
    right: newer.priority,
  };
};

const buildDataTableRow = (
  older: TestCaseVersion,
  newer: TestCaseVersion,
): CompareDataTableRow | null => {
  if (older.parameters.length === 0 && newer.parameters.length === 0) {
    return null;
  }

  const olderText = formatDataTableText(older.parameters, older.dataRows);
  const newerText = formatDataTableText(newer.parameters, newer.dataRows);
  if (checkIsSameDataTable(older, newer)) {
    return {
      kind: "unchanged",
      left: toTokens(olderText, "unchanged"),
      right: toTokens(newerText, "unchanged"),
    };
  }

  const tokens = buildWordDiff(olderText, newerText);

  return { kind: "changed", left: keepOlderTokens(tokens), right: keepNewerTokens(tokens) };
};

const sortSteps = (steps: readonly TestStep[]): TestStep[] => {
  return [...steps].sort((first, second) => first.order - second.order);
};

const checkIsSameStep = (first: TestStep, second: TestStep): boolean => {
  return (
    first.sharedStepKey === second.sharedStepKey &&
    first.action === second.action &&
    (first.expected ?? "") === (second.expected ?? "")
  );
};

const buildWholeSide = (step: TestStep, kind: DiffToken["kind"]): CompareStepSide => {
  return {
    order: step.order,
    action: toTokens(step.action ?? "", kind),
    expected: toTokens(step.expected ?? "", kind),
  };
};

const buildChangedRow = (older: TestStep, newer: TestStep): CompareStepRow => {
  const action = buildWordDiff(older.action ?? "", newer.action ?? "");
  const expected = buildWordDiff(older.expected ?? "", newer.expected ?? "");

  return {
    kind: "changed",
    left: {
      order: older.order,
      action: keepOlderTokens(action),
      expected: keepOlderTokens(expected),
    },
    right: {
      order: newer.order,
      action: keepNewerTokens(action),
      expected: keepNewerTokens(expected),
    },
  };
};

const buildReplacedRows = (
  removedSteps: readonly TestStep[],
  addedSteps: readonly TestStep[],
): CompareStepRow[] => {
  const pairCount = Math.min(removedSteps.length, addedSteps.length);
  const rows: CompareStepRow[] = [];

  for (let index = 0; index < pairCount; index += 1) {
    rows.push(buildChangedRow(removedSteps[index], addedSteps[index]));
  }

  for (const step of removedSteps.slice(pairCount)) {
    rows.push({ kind: "removed", left: buildWholeSide(step, "removed"), right: null });
  }

  for (const step of addedSteps.slice(pairCount)) {
    rows.push({ kind: "added", left: null, right: buildWholeSide(step, "added") });
  }

  return rows;
};

export const buildStepRows = (
  older: readonly TestStep[],
  newer: readonly TestStep[],
): CompareStepRow[] => {
  const olderSteps = sortSteps(older);
  const newerSteps = sortSteps(newer);
  const changes = diffArrays(olderSteps, newerSteps, { comparator: checkIsSameStep });
  const rows: CompareStepRow[] = [];
  let olderIndex = 0;
  let newerIndex = 0;
  let removedSteps: TestStep[] = [];
  let addedSteps: TestStep[] = [];

  const flushReplaced = (): void => {
    rows.push(...buildReplacedRows(removedSteps, addedSteps));
    removedSteps = [];
    addedSteps = [];
  };

  for (const change of changes) {
    const count = change.value.length;
    if (change.removed) {
      removedSteps.push(...olderSteps.slice(olderIndex, olderIndex + count));
      olderIndex += count;
    } else if (change.added) {
      addedSteps.push(...newerSteps.slice(newerIndex, newerIndex + count));
      newerIndex += count;
    } else {
      flushReplaced();
      for (let offset = 0; offset < count; offset += 1) {
        rows.push({
          kind: "unchanged",
          left: buildWholeSide(olderSteps[olderIndex + offset], "unchanged"),
          right: buildWholeSide(newerSteps[newerIndex + offset], "unchanged"),
        });
      }
      olderIndex += count;
      newerIndex += count;
    }
  }

  flushReplaced();

  return rows;
};

export const buildVersionComparison = (
  older: TestCaseVersion,
  newer: TestCaseVersion,
): VersionComparison => {
  const fields = TEXT_FIELDS.map((field) => {
    return buildTextRow(field, older[field] ?? "", newer[field] ?? "");
  });
  const priority = buildPriorityRow(older, newer);
  const dataTable = buildDataTableRow(older, newer);
  const steps = buildStepRows(older.steps, newer.steps);
  const changedRows = [...fields, priority, ...(dataTable === null ? [] : [dataTable]), ...steps];

  return {
    fields,
    priority,
    dataTable,
    steps,
    changeCount: changedRows.filter((row) => row.kind !== "unchanged").length,
  };
};
