"use client";

import { DSAlert, DSModal, DSStack, DSText } from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteEnvironment } from "../../hooks/mutations/use-delete-environment";
import type { Environment } from "../../typing/types/environment.type";

interface Props {
  projectKey: string;
  environment: Environment;
  onClose: () => void;
}

export const DeleteEnvironmentModal: FC<Props> = ({ projectKey, environment, onClose }) => {
  const { t } = useTranslation("environments");
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const deleteEnvironment = useDeleteEnvironment(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      showSuccessToast(t("toasts.deleted"));
      onClose();
    },
  });
  const isInUse = deleteEnvironment.error?.code === "ENVIRONMENT_IN_USE";

  const handleDelete = (): void => {
    deleteEnvironment.mutate(environment.id);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("delete.title")}
      isCloseDisabled={deleteEnvironment.isPending}
      action={{
        label: t("actions.delete"),
        type: "danger",
        icon: "trash",
        isLoading: deleteEnvironment.isPending,
        isDisabled: isInUse,
        onClick: handleDelete,
      }}
    >
      <DSStack gap={3}>
        <DSText>{t("delete.message", { name: environment.name })}</DSText>
        {deleteEnvironment.error !== null && (
          <DSAlert color="danger">
            {isInUse ? t("errors.inUse") : resolveMessage(deleteEnvironment.error)}
          </DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
