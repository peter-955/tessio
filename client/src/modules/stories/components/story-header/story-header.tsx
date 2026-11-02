"use client";

import { DSAlert, DSBadge, DSButton, DSButtonLink, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { ExportReportButton } from "@/modules/reports/components/export-report-button/export-report-button";
import { buildSprintPath } from "@/modules/sprints/utils/sprint-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useFormatDay } from "../../hooks/use-format-day";
import type { StoryDetail } from "../../typing/types/story.type";
import { buildStoriesPath } from "../../utils/story-path.util";
import { DeleteStoryModal } from "../delete-story-modal/delete-story-modal";
import { StoryEditorModal } from "../story-editor-modal/story-editor-modal";
import { StoryTestStatusBadge } from "../story-test-status-badge/story-test-status-badge";
import { TestStatusActions } from "../test-status-actions/test-status-actions";
import styles from "./story-header.module.scss";

interface Props {
  projectKey: string;
  story: StoryDetail;
}

type OpenedModal = "edit" | "delete" | null;

export const StoryHeader: FC<Props> = ({ projectKey, story }) => {
  const { t } = useTranslation("stories");
  const formatDate = useFormatDate();
  const formatDay = useFormatDay();
  const router = useRouter();
  const project = useCurrentProject();
  const [openedModal, setOpenedModal] = useState<OpenedModal>(null);
  const isWrittenInTessio = story.source === "tessio";
  const canEdit = isWrittenInTessio && checkHasProjectCapability(project, "story.edit");

  const closeModal = (): void => {
    setOpenedModal(null);
  };

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
            {isWrittenInTessio ? (
              <DSBadge color="gray">{t("detail.writtenInTessio")}</DSBadge>
            ) : (
              <>
                <span>{story.jiraIssueType}</span>
                <DSBadge color="gray">{story.jiraStatus}</DSBadge>
              </>
            )}
            <StoryTestStatusBadge status={story.testStatus} />
            {story.sprint === null ? (
              !isWrittenInTessio && <span>{t("detail.noSprint")}</span>
            ) : (
              <Link href={buildSprintPath(projectKey, story.sprint.id)}>{story.sprint.name}</Link>
            )}
            {isWrittenInTessio ? (
              <span>{t("detail.lastEdited", { date: formatDate(story.jiraUpdatedAt) })}</span>
            ) : (
              <span>{t("detail.lastSynced", { date: formatDate(story.syncedAt) })}</span>
            )}
          </span>
        }
        actions={
          <div className={styles.actions}>
            <TestStatusActions story={story} />
            <ExportReportButton target={{ source: "story", jiraKey: story.jiraKey }} />
            {canEdit && (
              <>
                <DSButton
                  type="default"
                  icon="edit"
                  onClick={() => {
                    setOpenedModal("edit");
                  }}
                >
                  {t("editor.edit")}
                </DSButton>
                <DSButton
                  type="default"
                  icon="trash"
                  onClick={() => {
                    setOpenedModal("delete");
                  }}
                >
                  {t("editor.delete")}
                </DSButton>
              </>
            )}
            {!isWrittenInTessio && (
              <DSButtonLink href={story.jiraUrl} type="default" isExternal>
                {t("detail.openInJira")}
              </DSButtonLink>
            )}
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
      {openedModal === "edit" && (
        <StoryEditorModal
          projectKey={projectKey}
          story={story}
          onClose={closeModal}
          onSaved={closeModal}
        />
      )}
      {openedModal === "delete" && (
        <DeleteStoryModal
          projectKey={projectKey}
          story={story}
          onClose={closeModal}
          onDeleted={() => {
            router.push(buildStoriesPath(projectKey));
          }}
        />
      )}
    </>
  );
};
