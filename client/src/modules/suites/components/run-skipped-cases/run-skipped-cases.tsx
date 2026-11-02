"use client";

import { DSBadge, DSCard, DSStack, DSText } from "@/components/design-system";
import { buildCasePath } from "@/modules/runs/utils/run-path.util";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SkippedRunCase } from "../../typing/types/suite.type";
import styles from "./run-skipped-cases.module.scss";

interface Props {
  projectKey: string;
  skippedCases: readonly SkippedRunCase[];
}

export const RunSkippedCases: FC<Props> = ({ projectKey, skippedCases }) => {
  const { t } = useTranslation("suites");

  if (skippedCases.length === 0) {
    return null;
  }

  return (
    <DSCard title={t("runs.skippedTitle")}>
      <DSStack gap={3}>
        <DSText size="sm" color="muted">
          {t("runs.skippedDescription")}
        </DSText>
        <ul className={styles.list} aria-label={t("runs.skippedLabel")}>
          {skippedCases.map((skippedCase) => {
            return (
              <li key={skippedCase.testCaseId} className={styles.item}>
                <Link href={buildCasePath(projectKey, skippedCase.code)} className={styles.code}>
                  {skippedCase.code}
                </Link>
                <span className={styles.title}>{skippedCase.title}</span>
                <DSText size="xs" color="muted" component="span">
                  {skippedCase.storyJiraKey}
                </DSText>
                <DSBadge color="yellow">{t(`skipReason.${skippedCase.reason}`)}</DSBadge>
              </li>
            );
          })}
        </ul>
      </DSStack>
    </DSCard>
  );
};
