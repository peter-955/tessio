"use client";

import { DSCard, DSTable } from "@/components/design-system";
import type { RunReport } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { listCountEntries } from "../../../utils/run-counts.util";
import { buildStoryPath } from "../../../utils/run-path.util";
import styles from "./report-stories.module.scss";

interface Props {
  projectKey: string;
  stories: NonNullable<RunReport["stories"]>;
}

export const ReportStories: FC<Props> = ({ projectKey, stories }) => {
  const { t } = useTranslation("runs");
  const { t: tSuites } = useTranslation("suites");

  if (stories.length === 0) {
    return null;
  }

  return (
    <DSCard title={tSuites("runs.reportStories")}>
      <DSTable label={tSuites("runs.reportStories")}>
        <thead>
          <tr>
            <th scope="col">{tSuites("runs.storyColumn")}</th>
            <th scope="col">{tSuites("runs.resultsColumn")}</th>
          </tr>
        </thead>
        <tbody>
          {stories.map((story) => {
            const countText = [
              t("counts.total", { count: story.counts.total }),
              ...listCountEntries(story.counts).map((entry) => {
                return t(`counts.${entry.key}`, { count: entry.count });
              }),
            ].join(" · ");

            return (
              <tr key={story.storyId}>
                <td>
                  <span className={styles.story}>
                    <Link href={buildStoryPath(projectKey, story.storyJiraKey)}>
                      {story.storyJiraKey}
                    </Link>
                    <span>{story.storyTitle}</span>
                  </span>
                </td>
                <td>{countText}</td>
              </tr>
            );
          })}
        </tbody>
      </DSTable>
    </DSCard>
  );
};
