"use client";

import { DSAlert, DSBadge, DSButtonLink, DSPageHeader } from "@/components/design-system";
import { buildSprintPath } from "@/modules/sprints/utils/sprint-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useFormatDay } from "../../hooks/use-format-day";
import type { StoryDetail } from "../../typing/types/story.type";
import { buildStoriesPath } from "../../utils/story-path.util";
import { StoryTestStatusBadge } from "../story-test-status-badge/story-test-status-badge";
import { TestStatusActions } from "../test-status-actions/test-status-actions";
import styles from "./story-header.module.scss";

interface Props {
  projectKey: string;
  story: StoryDetail;
}

export const StoryHeader: FC<Props> = ({ projectKey, story }) => {
  const { t } = useTranslation("stories");
  const formatDate = useFormatDate();
  const formatDay = useFormatDay();

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildStoriesPath(projectKey)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={`${story.jiraKey} · ${story.title}`}
        description={
          <span className={styles.details}>
            <span>{story.jiraIssueType}</span>
            <DSBadge color="gray">{story.jiraStatus}</DSBadge>
            <StoryTestStatusBadge status={story.testStatus} />
            {story.sprint === null ? (
              <span>{t("detail.noSprint")}</span>
            ) : (
              <Link href={buildSprintPath(projectKey, story.sprint.id)}>{story.sprint.name}</Link>
            )}
            <span>{t("detail.lastSynced", { date: formatDate(story.syncedAt) })}</span>
          </span>
        }
        actions={
          <div className={styles.actions}>
            <TestStatusActions story={story} />
            <DSButtonLink href={story.jiraUrl} type="default" isExternal>
              {t("detail.openInJira")}
            </DSButtonLink>
          </div>
        }
      />
      {story.jiraMissingAt !== null && (
        <div className={styles.alert}>
          <DSAlert color="warning" title={t("detail.missing.title")}>
            {t("detail.missing.body", { date: formatDay(story.jiraMissingAt) })}
          </DSAlert>
        </div>
      )}
    </>
  );
};
