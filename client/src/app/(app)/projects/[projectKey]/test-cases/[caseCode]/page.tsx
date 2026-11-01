import { TestCaseDetailPage } from "@/modules/test-cases/test-case-detail";
import { parseTestCaseTab } from "@/modules/test-cases/utils/test-case-tab.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Test case" };

const TestCaseRoute: FC<PageProps<"/projects/[projectKey]/test-cases/[caseCode]">> = async ({
  params,
  searchParams,
}) => {
  const { caseCode } = await params;
  const { tab } = await searchParams;

  return (
    <TestCaseDetailPage caseCode={caseCode.toUpperCase()} initialTab={parseTestCaseTab(tab)} />
  );
};

export default TestCaseRoute;
