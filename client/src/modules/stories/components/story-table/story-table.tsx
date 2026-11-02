"use client";

import { DSBadge, DSTable } from "@/components/design-system";
import type { StoryProgress } from "@/modules/traceability/typing/types/traceability.type";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { STORY_PROGRESS_COLUMNS } from "../../typing/constants/story.constant";
import type { StorySummary } from "../../typing/types/story.type";
import { buildStoryPath } from "../../utils/story-path.util";
import { StoryProgressCells } from "../story-progress-cells/story-progress-cells";
import { StoryTestStatusBadge } from "../story-test-status-badge/story-test-status-badge";
import styles from "./story-table.module.scss";

interface Props {
  projectKey: string;
  stories: StorySummary[];
  isSprintColumnShown: boolean;
  progressByStoryId: ReadonlyMap<string, StoryProgress> | undefined;
}

export const StoryTable: FC<Props> = ({
  projectKey,
  stories,
  isSprintColumnShown,
  progressByStoryId,
}) => {
  const { t } = useTranslation("stories");
  const { t: translateTraceability } = useTranslation("traceability");

  return (
    <DSTable label={t("title")}>
      <thead>
        <tr>
          <th scope="col">{t("columns.key")}</th>
          <th scope="col">{t("columns.title")}</th>
          {isSprintColumnShown && <th scope="col">{t("columns.sprint")}</th>}
          <th scope="col">{t("columns.jiraStatus")}</th>
          <th scope="col">{t("columns.testStatus")}</th>
          {STORY_PROGRESS_COLUMNS.map((column) => {
            return (
              <th
                key={column.label}
                scope="col"
                className={column.isNumeric ? styles.numeric : undefined}
              >
                {translateTraceability(`storyColumns.${column.label}`)}
              </th>
            );
          })}
          <th scope="col">{t("columns.jira")}</th>
        </tr>
      </thead>
      <tbody>
        {stories.map((story) => {
          return (
            <tr key={story.id}>
              <th scope="row">
                <Link href={buildStoryPath(projectKey, story.jiraKey)} className={styles.key}>
                  {story.jiraKey}
                </Link>
              </th>
              <td>
                <span className={styles.title}>
                  <span>{story.title}</span>
                  {story.jiraMissingAt !== null && (
                    <DSBadge color="yellow">{t("list.notInScope")}</DSBadge>
                  )}
                </span>
              </td>
              {isSprintColumnShown && (
                <td className={story.sprintName === null ? styles.muted : undefined}>
                  {story.sprintName ?? t("list.noSprint")}
                </td>
              )}
              <td className={story.source === "tessio" ? styles.muted : undefined}>
                {story.source === "tessio" ? (
                  t("list.writtenInTessio")
                ) : (
                  <DSBadge color="gray">{story.jiraStatus}</DSBadge>
                )}
              </td>
              <td>
                <StoryTestStatusBadge status={story.testStatus} />
              </td>
              <StoryProgressCells
                projectKey={projectKey}
                progress={progressByStoryId?.get(story.id)}
              />
              <td>
                {story.source === "jira" && (
                  <a href={story.jiraUrl} target="_blank" rel="noopener noreferrer">
                    {t("list.openInJira")}
                    <span className={styles.visuallyHidden}> {story.jiraKey}</span>
                  </a>
                )}
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
