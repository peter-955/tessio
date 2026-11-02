"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchWebhook } from "../../hooks/mutations/use-patch-webhook";
import type { Webhook } from "../../typing/types/webhook.type";

interface Props {
  projectKey: string;
  webhook: Webhook;
  onClose: () => void;
  onRotated: (webhook: Webhook, secret: string) => void;
}

export const RotateWebhookSecretModal: FC<Props> = ({
  projectKey,
  webhook,
  onClose,
  onRotated,
}) => {
  const { t } = useTranslation("integrations");
  const { showSuccessToast } = useShowToast();
  const rotateSecret = usePatchWebhook(projectKey, {
    onSuccess: (response) => {
      showSuccessToast(t("toasts.rotated"));
      if (response.secret === null) {
        onClose();
        return;
      }

      onRotated(response.webhook, response.secret);
    },
  });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("rotate.title")}
      isCloseDisabled={rotateSecret.isPending}
      action={{
        label: t("rotate.confirm"),
        type: "danger",
        isLoading: rotateSecret.isPending,
        onClick: () => {
          rotateSecret.mutate({ webhookId: webhook.id, body: { rotateSecret: true } });
        },
      }}
    >
      <DSText>{t("rotate.description", { url: webhook.url })}</DSText>
    </DSModal>
  );
};
