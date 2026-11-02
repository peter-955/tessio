import type {
  CaseCriterion,
  CaseDataValue,
  CaseFile,
} from "@/components/case-sheet/typing/types/case-sheet.type";
import type { DataItem } from "@/modules/test-data/typing/types/data-item.type";
import type { TestCaseDetail, TestFile } from "../typing/types/test-case.type";

export const buildCaseDataValues = (items: readonly DataItem[]): CaseDataValue[] => {
  return items
    .filter((item) => item.hasValue)
    .map((item): CaseDataValue => {
      return { key: item.key, kind: item.kind, value: item.kind === "secret" ? null : item.value };
    });
};

export const buildCaseCriteria = (detail: TestCaseDetail): CaseCriterion[] => {
  return detail.criteria
    .filter((criterion) => !criterion.isRemoved)
    .map((criterion): CaseCriterion => {
      return { code: criterion.code, text: criterion.text };
    });
};

export const buildTestFileReferences = (files: readonly TestFile[]): CaseFile[] => {
  return files.map((file): CaseFile => {
    return { key: file.key, fileName: file.currentVersion.fileName };
  });
};

export const buildCaseFiles = (detail: TestCaseDetail): CaseFile[] => {
  return buildTestFileReferences(detail.files);
};

export const mapRevealedValuesByKey = (
  items: readonly DataItem[],
  revealedValueById: Readonly<Record<string, string>>,
): Record<string, string> => {
  return Object.fromEntries(
    items.flatMap((item) => {
      const revealedValue = revealedValueById[item.id];

      return revealedValue === undefined ? [] : [[item.key, revealedValue]];
    }),
  );
};
