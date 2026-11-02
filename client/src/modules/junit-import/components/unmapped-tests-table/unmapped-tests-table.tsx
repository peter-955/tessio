"use client";

import { DSStack, DSTable, DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { UnmappedTest } from "../../typing/types/junit-import.type";
import styles from "./unmapped-tests-table.module.scss";

interface Props {
  tests: readonly UnmappedTest[];
  totalCount: number;
}

export const UnmappedTestsTable: FC<Props> = ({ tests, totalCount }) => {
  const { t } = useTranslation("junitImport");
  const hiddenCount = totalCount - tests.length;

  return (
    <DSStack gap={2}>
      <DSText size="sm" color="muted">
        {t("unmapped.description")}
      </DSText>
      <DSTable label={t("unmapped.tableLabel")}>
        <thead>
          <tr>
            <th scope="col">{t("unmapped.columns.test")}</th>
            <th scope="col">{t("unmapped.columns.result")}</th>
            <th scope="col">{t("unmapped.columns.reason")}</th>
          </tr>
        </thead>
        <tbody>
          {tests.map((test, index) => {
            return (
              <tr key={`${test.classname ?? ""}:${test.name}:${String(index)}`}>
                <th scope="row" className={styles.testCell}>
                  <span className={styles.name}>{test.name}</span>
                  {test.classname !== null && (
                    <DSText size="xs" color="muted" component="span" className={styles.classname}>
                      {test.classname}
                    </DSText>
                  )}
                </th>
                <td>
                  <StatusBadge status={test.status} />
                </td>
                <td className={styles.muted}>{t(`unmapped.reasons.${test.reason}`)}</td>
              </tr>
            );
          })}
        </tbody>
      </DSTable>
      {hiddenCount > 0 && (
        <DSText size="sm" color="muted">
          {t("unmapped.notListed", { count: hiddenCount })}
        </DSText>
      )}
    </DSStack>
  );
};
