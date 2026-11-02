"use client";

import { DSAlert, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { JunitImport } from "../../typing/types/junit-import.type";
import { UnmappedTestsTable } from "../unmapped-tests-table/unmapped-tests-table";

interface Props {
  result: JunitImport;
}

export const JunitImportResult: FC<Props> = ({ result }) => {
  const { t } = useTranslation("junitImport");
  const { counts } = result;

  return (
    <DSStack gap={4}>
      <DSAlert
        color={result.status === "passed" ? "success" : "warning"}
        title={t(`result.title.${result.status === "passed" ? "passed" : "failed"}`)}
      >
        {t("result.counts", {
          total: counts.total,
          passed: counts.passed,
          failed: counts.failed,
          skipped: counts.skipped,
        })}
      </DSAlert>
      <DSText size="sm">
        {t("result.mapped", { count: result.mappedTestCount })}
        {result.unmappedTestCount > 0 &&
          ` ${t("result.unmapped", { count: result.unmappedTestCount })}`}
      </DSText>
      {result.unmappedTestCount > 0 && (
        <UnmappedTestsTable tests={result.unmappedTests} totalCount={result.unmappedTestCount} />
      )}
    </DSStack>
  );
};
