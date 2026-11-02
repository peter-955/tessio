"use client";

import { buildCaseReferences } from "@/components/case-sheet/utils/case-references.util";
import { DSText } from "@/components/design-system";
import { countRunCases, groupRunCasesByStory } from "@/modules/suites/utils/run-story-group.util";
import type { RunCase, RunDetail } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import { useId, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { listCountEntries } from "../../utils/run-counts.util";
import { buildStoryPath } from "../../utils/run-path.util";
import { checkIsUntargetedRun } from "../../utils/run-target.util";
import { RunCaseCard } from "./run-case-card/run-case-card";
import styles from "./run-case-list.module.scss";

interface Props {
  projectKey: string;
  run: RunDetail;
}

export const RunCaseList: FC<Props> = ({ projectKey, run }) => {
  const { t } = useTranslation("runs");
  const { t: tSuites } = useTranslation("suites");
  const groupIdPrefix = useId();
  const isGroupedByStory = (run.testSuiteId ?? null) !== null || checkIsUntargetedRun(run);

  const renderCases = (cases: readonly RunCase[], label: string): ReactNode => {
    return (
      <ul className={styles.list} aria-label={label}>
        {cases.map((runCase) => {
          return (
            <RunCaseCard
              key={runCase.testCaseId}
              projectKey={projectKey}
              runCase={runCase}
              references={buildCaseReferences(run.data, runCase.files, {}, run.environmentName)}
              runStatus={run.status}
            />
          );
        })}
      </ul>
    );
  };

  if (!isGroupedByStory) {
    return renderCases(run.cases, t("case.listLabel"));
  }

  return (
    <div className={styles.groups} role="group" aria-label={tSuites("runs.storyGroupsLabel")}>
      {groupRunCasesByStory(run.cases).map((group, index) => {
        const headingId = `${groupIdPrefix}-${index}`;
        const heading =
          group.storyJiraKey === null
            ? tSuites("runs.otherCases")
            : tSuites("runs.storyHeading", { key: group.storyJiraKey, title: group.storyTitle });
        const countText = listCountEntries(countRunCases(group.cases))
          .map((entry) => {
            return t(`counts.${entry.key}`, { count: entry.count });
          })
          .join(" · ");

        return (
          <section key={group.key} className={styles.group} aria-labelledby={headingId}>
            <div className={styles.groupHeader}>
              <h3 id={headingId} className={styles.groupHeading}>
                {group.storyJiraKey === null ? (
                  heading
                ) : (
                  <Link href={buildStoryPath(projectKey, group.storyJiraKey)}>{heading}</Link>
                )}
              </h3>
              <DSText size="sm" color="muted" component="span">
                {countText}
              </DSText>
            </div>
            {renderCases(group.cases, heading)}
          </section>
        );
      })}
    </div>
  );
};
