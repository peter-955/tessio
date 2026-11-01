"use client";

import { DSBadge } from "@/components/design-system";
import {
  COVERAGE_HIGHLIGHT_COLORS,
  RUN_STATUS_COLORS,
} from "@/modules/traceability/typing/constants/traceability.constant";
import type { StoryProgress } from "@/modules/traceability/typing/types/traceability.type";
import { selectCoverageHighlight } from "@/modules/traceability/utils/coverage-highlight.util";
import { buildRunPath } from "@/modules/traceability/utils/run-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { STORY_PROGRESS_COLUMNS } from "../../typing/constants/story.constant";
import styles from "./story-progress-cells.module.scss";

interface Props {
  projectKey: string;
  progress: StoryProgress | undefined;
}

export const StoryProgressCells: FC<Props> = ({ projectKey, progress }) => {
  const { t: translateTraceability } = useTranslation("traceability");
  const formatDate = useFormatDate();

  if (progress === undefined) {
    return (
      <>
        {STORY_PROGRESS_COLUMNS.map((column) => {
          return (
            <td key={column.label} className={column.isNumeric ? styles.numeric : undefined}>
              <span aria-hidden="true" className={styles.muted}>
                —
              </span>
              <span className={styles.visuallyHidden}>
                {translateTraceability("storyColumns.unknown")}
              </span>
            </td>
          );
        })}
      </>
    );
  }

  const { coverage, lastRun } = progress;
  const highlight = selectCoverageHighlight(coverage);

  return (
    <>
      <td className={styles.numeric}>
        {coverage.criterionCount === 0 ? (
          <span className={styles.muted}>—</span>
        ) : (
          <span className={styles.coverage}>
            <span>
              {translateTraceability("storyColumns.coverageValue", {
                covered: coverage.coveredCount,
                total: coverage.criterionCount,
              })}
            </span>
            {highlight !== null && (
              <DSBadge color={COVERAGE_HIGHLIGHT_COLORS[highlight.kind]}>
                {translateTraceability(`storyColumns.${highlight.kind}`, {
                  count: highlight.count,
                })}
              </DSBadge>
            )}
          </span>
        )}
      </td>
      <td className={styles.numeric}>
        {progress.openGapCount > 0 ? (
          <DSBadge color="yellow">{progress.openGapCount}</DSBadge>
        ) : (
          progress.openGapCount
        )}
      </td>
      <td className={styles.numeric}>
        {progress.activeFailureCount > 0 ? (
          <DSBadge color="red">{progress.activeFailureCount}</DSBadge>
        ) : (
          progress.activeFailureCount
        )}
      </td>
      <td>
        {lastRun === null ? (
          <span className={styles.muted}>{translateTraceability("storyColumns.noRun")}</span>
        ) : (
          <span className={styles.lastRun}>
            <Link href={buildRunPath(projectKey, lastRun.id)}>
              <DSBadge color={RUN_STATUS_COLORS[lastRun.status]} hasDot>
                {translateTraceability(`runStatus.${lastRun.status}`)}
              </DSBadge>
            </Link>
            <span className={styles.muted}>
              {formatDate(lastRun.finishedAt ?? lastRun.startedAt)}
            </span>
          </span>
        )}
      </td>
    </>
  );
};
