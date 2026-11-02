"use client";

import { DSAlert, DSButton, DSEmptyState, DSPageHeader, DSStack } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useHasProjectCapability } from "@/components/project-context/hooks/use-has-project-capability";
import { ReviewSettingsCard } from "@/modules/case-review/components/review-settings-card/review-settings-card";
import { ChatChannelsCard } from "@/modules/chat-channels/components/chat-channels-card/chat-channels-card";
import { LabelManagerCard } from "@/modules/labels/components/label-manager-card/label-manager-card";
import { WebhooksCard } from "@/modules/webhooks/components/webhooks-card/webhooks-card";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { AllowedFileTypesCard } from "./components/allowed-file-types-card/allowed-file-types-card";
import { ArchiveProjectCard } from "./components/archive-project-card/archive-project-card";
import { ArchiveProjectModal } from "./components/archive-project-modal/archive-project-modal";
import { DefaultEnvironmentCard } from "./components/default-environment-card/default-environment-card";
import { GeneralSettingsCard } from "./components/general-settings-card/general-settings-card";
import { useIsWorkspaceAdmin } from "./hooks/use-is-workspace-admin";

export const ProjectSettingsPage: FC = () => {
  const { t } = useTranslation("projects");
  const project = useCurrentProject();
  const canEdit = useHasProjectCapability("project.edit");
  const canEditLabels = useHasProjectCapability("test_case.edit");
  const canManageChatChannels =
    useHasProjectCapability("integration.manage") && !project.isArchived;
  const canManageWebhooks = useHasProjectCapability("integration.manage") && !project.isArchived;
  const isWorkspaceAdmin = useIsWorkspaceAdmin();
  const [isUnarchiveModalOpened, setIsUnarchiveModalOpened] = useState(false);

  const renderContent = (): ReactNode => {
    if (canEdit) {
      return (
        <DSStack gap={5}>
          <GeneralSettingsCard project={project} />
          <DefaultEnvironmentCard project={project} />
          <AllowedFileTypesCard project={project} />
          <LabelManagerCard
            projectKey={project.key}
            canManage={canEditLabels && !project.isArchived}
          />
          <ReviewSettingsCard project={project} />
          {canManageChatChannels && <ChatChannelsCard projectKey={project.key} />}
          {canManageWebhooks && <WebhooksCard projectKey={project.key} />}
          {isWorkspaceAdmin && <ArchiveProjectCard project={project} />}
        </DSStack>
      );
    }

    if (project.isArchived) {
      return (
        <DSAlert
          color="info"
          title={t("settings.readOnlyArchived")}
          action={
            isWorkspaceAdmin && (
              <DSButton
                type="primary"
                icon="restore"
                onClick={() => {
                  setIsUnarchiveModalOpened(true);
                }}
              >
                {t("list.actions.unarchive")}
              </DSButton>
            )
          }
        >
          {t("archive.body")}
        </DSAlert>
      );
    }

    return <DSEmptyState title={t("settings.needsAdmin")} icon="lock" />;
  };

  return (
    <>
      <DSPageHeader title={t("settings.title")} description={t("settings.description")} />
      {renderContent()}
      {isWorkspaceAdmin && project.isArchived && (
        <ArchiveProjectModal
          target={{ project, mode: "unarchive" }}
          isOpened={isUnarchiveModalOpened}
          onClose={() => {
            setIsUnarchiveModalOpened(false);
          }}
        />
      )}
    </>
  );
};
