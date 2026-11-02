"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteWebhook } from "../../hooks/mutations/use-delete-webhook";
import type { Webhook } from "../../typing/types/webhook.type";

interface Props {
  projectKey: string;
  webhook: Webhook;
  onClose: () => void;
}

export const DeleteWebhookModal: FC<Props> = ({ projectKey, webhook, onClose }) => {
  const { t } = useTranslation("integrations");
  const { showSuccessToast } = useShowToast();
  const deleteWebhook = useDeleteWebhook(projectKey, {
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
      isCloseDisabled={deleteWebhook.isPending}
      action={{
        label: t("delete.confirm"),
        type: "danger",
        isLoading: deleteWebhook.isPending,
        onClick: () => {
          deleteWebhook.mutate(webhook.id);
        },
      }}
    >
      <DSText>{t("delete.description", { url: webhook.url })}</DSText>
    </DSModal>
  );
};
