"use client";

import { DSAlert, DSModal, DSStack, DSText } from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteLabel } from "../../hooks/mutations/use-delete-label";
import type { Label } from "../../typing/types/label.type";

interface Props {
  projectKey: string;
  label: Label;
  onClose: () => void;
}

export const DeleteLabelModal: FC<Props> = ({ projectKey, label, onClose }) => {
  const { t } = useTranslation("labels");
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const deleteLabel = useDeleteLabel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      showSuccessToast(t("toasts.deleted"));
      onClose();
    },
  });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("delete.title")}
      isCloseDisabled={deleteLabel.isPending}
      action={{
        label: t("delete.confirm"),
        type: "danger",
        icon: "trash",
        isLoading: deleteLabel.isPending,
        onClick: () => {
          deleteLabel.mutate(label.id);
        },
      }}
    >
      <DSStack gap={3}>
        <DSText>{t("delete.message", { name: label.name, count: label.caseCount })}</DSText>
        {deleteLabel.error !== null && (
          <DSAlert color="danger">
            {deleteLabel.error.code === "NOT_FOUND"
              ? t("errors.notFound")
              : resolveMessage(deleteLabel.error)}
          </DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
