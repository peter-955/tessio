"use client";

import { DSBadge } from "@/components/design-system";
import { LabelChips } from "@/modules/labels/components/label-chips/label-chips";
import { buildStoryPath } from "@/modules/stories/utils/story-path.util";
import { ResultStatusBadge } from "@/modules/traceability/components/result-status-badge/result-status-badge";
import type { LatestResult } from "@/modules/traceability/typing/types/traceability.type";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TestCaseColumn } from "../../../typing/enums/test-case-column.enum";
import type { TestCaseSummary } from "../../../typing/types/test-case.type";
import { buildTestCasePath } from "../../../utils/test-case-path.util";
import { FlakyCaseBadges } from "../../flaky-case-badges/flaky-case-badges";
import { TestCasePriorityBadge } from "../../test-case-priority-badge/test-case-priority-badge";
import { TestCaseStatusBadge } from "../../test-case-status-badge/test-case-status-badge";
import styles from "./test-case-table-cell.module.scss";

interface Props {
  column: TestCaseColumn;
  projectKey: string;
  testCase: TestCaseSummary;
  latestResult: LatestResult | null | undefined;
}

export const TestCaseTableCell: FC<Props> = ({ column, projectKey, testCase, latestResult }) => {
  const { t } = useTranslation("testCases");
  const { t: translateTraceability } = useTranslation("traceability");
  const formatDate = useFormatDate();

  switch (column) {
    case TestCaseColumn.CODE:
      return (
        <th scope="row">
          <Link href={buildTestCasePath(projectKey, testCase.code)} className={styles.code}>
            {testCase.code}
          </Link>
        </th>
      );
    case TestCaseColumn.TITLE:
      return (
        <td className={styles.title}>
          {testCase.title}
          <LabelChips labels={testCase.labels} className={styles.labels} />
        </td>
      );
    case TestCaseColumn.STORY:
      return (
        <td>
          <Link href={buildStoryPath(projectKey, testCase.storyKey)} className={styles.code}>
            {testCase.storyKey}
          </Link>
        </td>
      );
    case TestCaseColumn.PRIORITY:
      return (
        <td>
          <TestCasePriorityBadge priority={testCase.priority} />
        </td>
      );
    case TestCaseColumn.STATUS:
      return (
        <td>
          <span className={styles.status}>
            <TestCaseStatusBadge status={testCase.status} />
            {testCase.needsReview && <DSBadge color="yellow">{t("table.needsReview")}</DSBadge>}
            <FlakyCaseBadges flags={testCase} />
          </span>
        </td>
      );
    case TestCaseColumn.LATEST_RESULT:
      return (
        <td>
          {latestResult === undefined ? (
            <>
              <span aria-hidden="true" className={styles.muted}>
                —
              </span>
              <span className={styles.visuallyHidden}>
                {translateTraceability("storyColumns.unknown")}
              </span>
            </>
          ) : (
            <ResultStatusBadge result={latestResult} />
          )}
        </td>
      );
    case TestCaseColumn.STEPS:
      return <td className={styles.numeric}>{testCase.stepCount}</td>;
    case TestCaseColumn.CRITERIA:
      return <td className={styles.numeric}>{testCase.criterionIds.length}</td>;
    case TestCaseColumn.LAST_SAVED:
      return <td className={styles.muted}>{formatDate(testCase.lastSavedAt)}</td>;
  }
};
