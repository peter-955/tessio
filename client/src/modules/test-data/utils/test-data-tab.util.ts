import { TestDataTab } from "../typing/enums/test-data-tab.enum";

const TEST_DATA_TABS: readonly string[] = Object.values(TestDataTab);

const isTestDataTab = (value: string): value is TestDataTab => {
  return TEST_DATA_TABS.includes(value);
};

export const parseTestDataTab = (value: string | string[] | undefined): TestDataTab => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue !== undefined && isTestDataTab(firstValue) ? firstValue : TestDataTab.DATA;
};
