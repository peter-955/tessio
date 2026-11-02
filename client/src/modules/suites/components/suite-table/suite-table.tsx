"use client";

import { DSBadge, DSTable, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SuiteSummary } from "../../typing/types/suite.type";
import { buildSuitePath } from "../../utils/suite-path.util";
import { SuiteLastRun } from "../suite-last-run/suite-last-run";
import styles from "./suite-table.module.scss";

interface Props {
  projectKey: string;
  suites: SuiteSummary[];
}

export const SuiteTable: FC<Props> = ({ projectKey, suites }) => {
  const { t } = useTranslation("suites");
  const formatDate = useFormatDate();

  return (
    <DSTable label={t("list.tableLabel")}>
      <caption className={styles.caption}>{t("list.tableLabel")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("list.columns.name")}</th>
          <th scope="col">{t("list.columns.cases")}</th>
          <th scope="col">{t("list.columns.lastRun")}</th>
          <th scope="col">{t("list.columns.created")}</th>
        </tr>
      </thead>
      <tbody>
        {suites.map((suite) => {
          return (
            <tr key={suite.id}>
              <td>
                <div className={styles.name}>
                  <span className={styles.title}>
                    <Link href={buildSuitePath(projectKey, suite.id)}>{suite.name}</Link>
                    {suite.archivedAt !== null && (
                      <DSBadge color="gray">{t("list.archived")}</DSBadge>
                    )}
                  </span>
                  {suite.description !== null && (
                    <DSText size="xs" color="muted" component="span" className={styles.description}>
                      {suite.description}
                    </DSText>
                  )}
                </div>
              </td>
              <td>
                <div className={styles.stacked}>
                  <span>{t("list.caseCount", { count: suite.caseCount })}</span>
                  <DSText size="xs" color="muted" component="span">
                    {t("list.readyCount", { count: suite.readyCaseCount })}
                  </DSText>
                </div>
              </td>
              <td>
                <SuiteLastRun projectKey={projectKey} run={suite.lastRun} />
              </td>
              <td className={styles.muted}>{formatDate(suite.createdAt)}</td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
