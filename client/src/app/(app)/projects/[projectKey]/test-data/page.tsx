import { TestDataPage } from "@/modules/test-data/test-data";
import { parseTestDataTab } from "@/modules/test-data/utils/test-data-tab.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Test data" };

const TestDataRoute: FC<PageProps<"/projects/[projectKey]/test-data">> = async ({
  searchParams,
}) => {
  const { tab } = await searchParams;

  return <TestDataPage initialTab={parseTestDataTab(tab)} />;
};

export default TestDataRoute;
