import { UUID_PATTERN } from "../typing/constants/manual-run.constant";

export const parseInitialSuiteId = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;
  const suiteId = firstValue?.trim().toLowerCase() ?? "";

  return UUID_PATTERN.test(suiteId) ? suiteId : null;
};
