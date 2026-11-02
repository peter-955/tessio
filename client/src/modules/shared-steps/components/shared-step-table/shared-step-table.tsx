"use client";

import { DSBadge, DSCode, DSTable } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SharedStep } from "../../typing/types/shared-step.type";
import { buildSharedStepPath } from "../../utils/shared-step-path.util";
import styles from "./shared-step-table.module.scss";

interface Props {
  projectKey: string;
  sharedSteps: SharedStep[];
}

export const SharedStepTable: FC<Props> = ({ projectKey, sharedSteps }) => {
  const { t } = useTranslation("sharedSteps");
  const formatDate = useFormatDate();

  return (
    <DSTable label={t("list.tableLabel")}>
      <caption className={styles.caption}>{t("list.tableLabel")}</caption>
      <thead>
        <tr>
          <th scope="col">{t("list.columns.title")}</th>
          <th scope="col">{t("list.columns.key")}</th>
          <th scope="col">{t("list.columns.steps")}</th>
          <th scope="col">{t("list.columns.usage")}</th>
          <th scope="col">{t("list.columns.version")}</th>
        </tr>
      </thead>
      <tbody>
        {sharedSteps.map((sharedStep) => {
          return (
            <tr key={sharedStep.id}>
              <td>
                <span className={styles.title}>
                  <Link href={buildSharedStepPath(projectKey, sharedStep.key)}>
                    {sharedStep.title}
                  </Link>
                  {sharedStep.isArchived && <DSBadge color="gray">{t("list.archived")}</DSBadge>}
                </span>
              </td>
              <td>
                <DSCode>{sharedStep.key}</DSCode>
              </td>
              <td className={styles.nowrap}>
                {t("list.stepCount", { count: sharedStep.currentVersion.steps.length })}
              </td>
              <td className={styles.nowrap}>
                {t("usage.count", { count: sharedStep.usageCount })}
              </td>
              <td className={styles.muted}>
                {t("list.versionOn", {
                  number: sharedStep.currentVersion.number,
                  date: formatDate(sharedStep.currentVersion.createdAt),
                })}
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
