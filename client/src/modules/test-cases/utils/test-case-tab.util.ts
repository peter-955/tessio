import { TestCaseDetailTab } from "../typing/enums/test-case-detail-tab.enum";

const TEST_CASE_DETAIL_TABS: readonly string[] = Object.values(TestCaseDetailTab);

const isTestCaseDetailTab = (value: string): value is TestCaseDetailTab => {
  return TEST_CASE_DETAIL_TABS.includes(value);
};

export const parseTestCaseTab = (value: string | string[] | undefined): TestCaseDetailTab => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue !== undefined && isTestCaseDetailTab(firstValue)
    ? firstValue
    : TestCaseDetailTab.DETAILS;
};
