"use client";

import { DSTable, DSText } from "@/components/design-system";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { FlakyCaseBadges } from "@/modules/test-cases/components/flaky-case-badges/flaky-case-badges";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetTopFailingCases } from "../../hooks/queries/use-get-top-failing-cases";
import { useInsightFormatters } from "../../hooks/use-insight-formatters";
import type { InsightsRange } from "../../typing/types/insights-range.type";
import { InsightPanel } from "../insight-panel/insight-panel";
import styles from "./failing-cases-card.module.scss";

interface Props {
  projectKey: string;
  range: InsightsRange;
}

export const FailingCasesCard: FC<Props> = ({ projectKey, range }) => {
  const { t } = useTranslation("insights");
  const formatDate = useFormatDate();
  const { formatShare } = useInsightFormatters();
  const { data, isPending, isError, isFetching, refetch } = useGetTopFailingCases(
    projectKey,
    range,
  );

  return (
    <InsightPanel
      title={t("topFailing.title")}
      description={t("topFailing.description")}
      state={{ isPending, isError, isFetching, refetch }}
      isEmpty={data !== undefined && data.length === 0}
      emptyTitle={t("topFailing.emptyTitle")}
      emptyDescription={t("topFailing.emptyDescription")}
      renderContent={() => {
        return (
          <DSTable label={t("topFailing.title")}>
            <thead>
              <tr>
                <th scope="col">{t("cases.columns.case")}</th>
                <th scope="col">{t("cases.columns.story")}</th>
                <th scope="col">{t("topFailing.columns.failures")}</th>
                <th scope="col">{t("topFailing.columns.failRate")}</th>
                <th scope="col">{t("topFailing.columns.lastFailed")}</th>
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
                          <FlakyCaseBadges
                            flags={{
                              isFlaky: item.isFlaky,
                              isDisagreeing: false,
                              isQuarantined: item.isQuarantined,
                            }}
                          />
                        </span>
                      </span>
                    </td>
                    <td>
                      <Link href={buildStoryPath(projectKey, item.storyJiraKey)}>
                        {item.storyJiraKey}
                      </Link>
                    </td>
                    <td className={styles.numeric}>
                      {t("topFailing.failuresValue", {
                        failed: item.failedCount,
                        blocked: item.blockedCount,
                        total: item.resultCount,
                      })}
                    </td>
                    <td className={styles.numeric}>{formatShare(item.failRate)}</td>
                    <td>{formatDate(item.lastFailedAt)}</td>
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
