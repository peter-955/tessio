"use client";

import {
  DSAlert,
  DSBadge,
  DSButton,
  DSButtonLink,
  DSCard,
  DSCode,
  DSPageHeader,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchSharedStep } from "../../hooks/mutations/use-patch-shared-step";
import { useSharedStepApiErrors } from "../../hooks/use-shared-step-api-errors";
import type { SharedStep } from "../../typing/types/shared-step.type";
import { buildSharedStepsPath } from "../../utils/shared-step-path.util";
import { checkCanEditSharedSteps } from "../../utils/shared-step-permission.util";
import { SharedStepActions } from "../shared-step-actions/shared-step-actions";
import { SharedStepFormModal } from "../shared-step-form-modal/shared-step-form-modal";
import { SharedStepUsageList } from "../shared-step-usage-list/shared-step-usage-list";
import styles from "./shared-step-detail-view.module.scss";

interface Props {
  sharedStep: SharedStep;
}

export const SharedStepDetailView: FC<Props> = ({ sharedStep }) => {
  const { t } = useTranslation("sharedSteps");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSharedStepApiErrors();
  const [isEditOpened, setIsEditOpened] = useState(false);
  const canEdit = checkCanEditSharedSteps(project);
  const archiveSharedStep = usePatchSharedStep(project.key, {
    isGlobalErrorToastDisabled: true,
    onError: (error: ApiError) => {
      showErrorToast(resolveMessage(error, apiErrors));
    },
    onSuccess: (savedStep) => {
      showSuccessToast(
        savedStep.isArchived
          ? t("toasts.archived", { title: savedStep.title })
          : t("toasts.restored", { title: savedStep.title }),
      );
    },
  });

  const toggleArchived = (): void => {
    archiveSharedStep.mutate({
      key: sharedStep.key,
      body: {
        baseVersionNumber: sharedStep.currentVersion.number,
        archived: !sharedStep.isArchived,
      },
    });
  };

  const actions = canEdit && (
    <>
      {!sharedStep.isArchived && (
        <DSButton
          type="outline"
          icon="edit"
          onClick={() => {
            setIsEditOpened(true);
          }}
        >
          {t("detail.edit")}
        </DSButton>
      )}
      <DSButton
        type="default"
        icon={sharedStep.isArchived ? "restore" : "archive"}
        isLoading={archiveSharedStep.isPending}
        onClick={toggleArchived}
      >
        {sharedStep.isArchived ? t("detail.restore") : t("detail.archive")}
      </DSButton>
    </>
  );

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildSharedStepsPath(project.key)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={sharedStep.title}
        description={
          <span className={styles.meta}>
            <DSCode>{sharedStep.key}</DSCode>
            {sharedStep.isArchived && <DSBadge color="gray">{t("list.archived")}</DSBadge>}
            <span>
              {t("detail.version", {
                number: sharedStep.currentVersion.number,
                date: formatDate(sharedStep.currentVersion.createdAt),
              })}
            </span>
          </span>
        }
        actions={actions}
      />
      <DSStack gap={5}>
        {sharedStep.isArchived && <DSAlert color="info">{t("detail.archivedNotice")}</DSAlert>}
        <DSCard title={t("detail.stepsTitle")}>
          <DSStack gap={3}>
            {sharedStep.currentVersion.dataKeys.length > 0 && (
              <DSText size="sm" color="muted">
                {t("detail.dataKeys", { keys: sharedStep.currentVersion.dataKeys.join(", ") })}
              </DSText>
            )}
            <SharedStepActions
              actions={sharedStep.currentVersion.steps}
              ariaLabel={t("reference.stepsOf", { title: sharedStep.title })}
            />
          </DSStack>
        </DSCard>
        <DSCard title={t("usage.count", { count: sharedStep.usageCount })}>
          <DSStack gap={3}>
            <DSText size="sm" color="muted">
              {t("usage.description")}
            </DSText>
            <SharedStepUsageList projectKey={project.key} sharedStepKey={sharedStep.key} />
          </DSStack>
        </DSCard>
      </DSStack>
      {isEditOpened && (
        <SharedStepFormModal
          projectKey={project.key}
          sharedStep={sharedStep}
          onClose={() => {
            setIsEditOpened(false);
          }}
        />
      )}
    </>
  );
};
