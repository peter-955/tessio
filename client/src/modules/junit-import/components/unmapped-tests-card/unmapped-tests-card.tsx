"use client";

import { DSCard } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { UnmappedTest } from "../../typing/types/junit-import.type";
import { UnmappedTestsTable } from "../unmapped-tests-table/unmapped-tests-table";

interface Props {
  tests: readonly UnmappedTest[];
  totalCount: number;
}

export const UnmappedTestsCard: FC<Props> = ({ tests, totalCount }) => {
  const { t } = useTranslation("junitImport");

  if (totalCount === 0) {
    return null;
  }

  return (
    <DSCard title={t("unmapped.title", { count: totalCount })}>
      <UnmappedTestsTable tests={tests} totalCount={totalCount} />
    </DSCard>
  );
};
