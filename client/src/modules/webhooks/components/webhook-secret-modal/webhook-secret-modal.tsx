"use client";

import { DSAlert, DSCode, DSModal, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Webhook } from "../../typing/types/webhook.type";

interface Props {
  webhook: Webhook;
  secret: string;
  onClose: () => void;
}

export const WebhookSecretModal: FC<Props> = ({ webhook, secret, onClose }) => {
  const { t } = useTranslation("integrations");

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("secret.title")}
      hasCancelButton={false}
      isClosedOnClickOutside={false}
      action={{ label: t("secret.done"), onClick: onClose }}
    >
      <DSStack gap={4}>
        <DSAlert color="warning">{t("secret.shownOnce")}</DSAlert>
        <DSText size="sm" color="muted">
          {webhook.url}
        </DSText>
        <DSCode isBlock isCopyable>
          {secret}
        </DSCode>
        <DSText size="sm">{t("secret.explanation")}</DSText>
      </DSStack>
    </DSModal>
  );
};
