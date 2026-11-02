import type { DSSelectOption } from "@/components/design-system";
import type { SuiteSummary } from "../typing/types/suite.type";

export type SuiteOptionSource = Pick<SuiteSummary, "id" | "name" | "archivedAt">;

export const buildSuiteOptions = (
  suites: readonly SuiteOptionSource[],
  value: string | null,
  toArchivedLabel: (name: string) => string,
  selectedSuite: SuiteOptionSource | null = null,
): DSSelectOption<string>[] => {
  const toOption = (suite: SuiteOptionSource): DSSelectOption<string> => {
    return {
      value: suite.id,
      label: suite.archivedAt === null ? suite.name : toArchivedLabel(suite.name),
    };
  };
  const options = suites.map(toOption);
  const isValueListed = options.some((option) => {
    return option.value === value;
  });

  if (value === null || isValueListed || selectedSuite?.id !== value) {
    return options;
  }

  return [toOption(selectedSuite), ...options];
};
