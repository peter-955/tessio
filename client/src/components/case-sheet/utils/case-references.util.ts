import type { CaseDataValue, CaseFile, CaseReferences } from "../typing/types/case-sheet.type";

export const buildCaseReferences = (
  dataValues: readonly CaseDataValue[],
  files: readonly CaseFile[],
  revealedValues: Readonly<Record<string, string>>,
  environmentName: string | null,
): CaseReferences => {
  return {
    dataByKey: new Map(
      dataValues.map((dataValue) => {
        return [dataValue.key, dataValue];
      }),
    ),
    filesByKey: new Map(
      files.map((file) => {
        return [file.key, file];
      }),
    ),
    revealedValues,
    environmentName,
  };
};
