"use client";

import { DSTable } from "@/components/design-system";
import type { LatestResult } from "@/modules/traceability/typing/types/traceability.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_CASE_COLUMNS } from "../../typing/constants/test-case-table.constant";
import { TestCaseColumn } from "../../typing/enums/test-case-column.enum";
import type { TestCaseSummary } from "../../typing/types/test-case.type";
import { TestCaseTableCell } from "./test-case-table-cell/test-case-table-cell";
import styles from "./test-case-table.module.scss";

interface Props {
  projectKey: string;
  testCases: TestCaseSummary[];
  isStoryColumnShown: boolean;
  latestResultByCaseId: ReadonlyMap<string, LatestResult | null> | undefined;
}

export const TestCaseTable: FC<Props> = ({
  projectKey,
  testCases,
  isStoryColumnShown,
  latestResultByCaseId,
}) => {
  const { t } = useTranslation("testCases");
  const { t: translateTraceability } = useTranslation("traceability");
  const columns = TEST_CASE_COLUMNS.filter((definition) => {
    return isStoryColumnShown || definition.column !== TestCaseColumn.STORY;
  });

  return (
    <DSTable label={t("table.ariaLabel")}>
      <caption className={styles.caption}>{t("table.ariaLabel")}</caption>
      <thead>
        <tr>
          {columns.map((definition) => {
            return (
              <th
                key={definition.column}
                scope="col"
                className={definition.isNumeric ? styles.numeric : undefined}
              >
                {definition.namespace === "traceability"
                  ? translateTraceability(`caseColumns.${definition.label}`)
                  : t(`table.${definition.label}`)}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {testCases.map((testCase) => {
          return (
            <tr key={testCase.id}>
              {columns.map((definition) => {
                return (
                  <TestCaseTableCell
                    key={definition.column}
                    column={definition.column}
                    projectKey={projectKey}
                    testCase={testCase}
                    latestResult={latestResultByCaseId?.get(testCase.id)}
                  />
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
