"use client";

import { DSTable, DSText } from "@/components/design-system";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { FlakyCaseBadges } from "@/modules/test-cases/components/flaky-case-badges/flaky-case-badges";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetFlakyCases } from "../../hooks/queries/use-get-flaky-cases";
import type { FlakyCase } from "../../typing/types/insights.type";
import { InsightPanel } from "../insight-panel/insight-panel";
import styles from "./flaky-cases-card.module.scss";

interface Props {
  projectKey: string;
}

export const FlakyCasesCard: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("insights");
  const formatDate = useFormatDate();
  const { data, isPending, isError, isFetching, refetch } = useGetFlakyCases(projectKey);

  const describeSince = (item: FlakyCase): string => {
    const since = item.flakySince ?? item.disagreedAt;

    return since === null ? t("noValue") : formatDate(since);
  };

  return (
    <InsightPanel
      title={t("flaky.title")}
      description={t("flaky.description")}
      state={{ isPending, isError, isFetching, refetch }}
      isEmpty={data !== undefined && data.length === 0}
      emptyTitle={t("flaky.emptyTitle")}
      emptyDescription={t("flaky.emptyDescription")}
      renderContent={() => {
        return (
          <DSTable label={t("flaky.title")}>
            <thead>
              <tr>
                <th scope="col">{t("cases.columns.case")}</th>
                <th scope="col">{t("cases.columns.story")}</th>
                <th scope="col">{t("flaky.columns.flips")}</th>
                <th scope="col">{t("flaky.columns.since")}</th>
              </tr>
            </thead>
            <tbody>
              {(data ?? []).map((item) => {
                return (
                  <tr key={item.testCaseId}>
                    <td>
                      <span className={styles.case}>
                        <Link href={buildTestCasePath(projectKey, item.code)}>{item.code}</Link>
                        <DSText size="sm" component="span" className={styles.title}>
                          {item.title}
                        </DSText>
                        <span className={styles.badges}>
                          <FlakyCaseBadges flags={item} />
                        </span>
                      </span>
                    </td>
                    <td>
                      <Link href={buildStoryPath(projectKey, item.storyJiraKey)}>
                        {item.storyJiraKey}
                      </Link>
                    </td>
                    <td className={styles.numeric}>
                      {t("flaky.flipsValue", { count: item.flakyScore })}
                    </td>
                    <td>{describeSince(item)}</td>
                  </tr>
                );
              })}
            </tbody>
          </DSTable>
        );
      }}
    />
  );
};
