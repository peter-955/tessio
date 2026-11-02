"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { WEBHOOK_DELIVERY_STATUS_COLORS } from "../../typing/constants/webhook.constant";
import type { WebhookDeliveryStatus } from "../../typing/types/webhook.type";

interface Props {
  status: WebhookDeliveryStatus;
}

export const WebhookDeliveryStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("integrations");

  return (
    <DSBadge color={WEBHOOK_DELIVERY_STATUS_COLORS[status]}>
      {t(`deliveries.status.${status}`)}
    </DSBadge>
  );
};
