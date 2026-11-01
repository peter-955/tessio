import { TestCasesPage } from "@/modules/test-cases/test-cases";
import { parseTestCaseFilters } from "@/modules/test-cases/utils/test-case-filters.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Test cases" };

const TestCasesRoute: FC<PageProps<"/projects/[projectKey]/test-cases">> = async ({
  searchParams,
}) => {
  return <TestCasesPage initialFilters={parseTestCaseFilters(await searchParams)} />;
};

export default TestCasesRoute;
