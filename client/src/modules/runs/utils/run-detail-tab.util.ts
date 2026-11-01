import { RunDetailTab } from "../typing/enums/run-detail-tab.enum";

const RUN_DETAIL_TABS: readonly string[] = Object.values(RunDetailTab);

const isRunDetailTab = (value: string): value is RunDetailTab => {
  return RUN_DETAIL_TABS.includes(value);
};

export const parseRunDetailTab = (value: string | string[] | null | undefined): RunDetailTab => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return typeof firstValue === "string" && isRunDetailTab(firstValue)
    ? firstValue
    : RunDetailTab.RESULTS;
};
