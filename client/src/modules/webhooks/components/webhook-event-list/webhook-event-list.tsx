"use client";

import { DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { WEBHOOK_EVENTS, WEBHOOK_EVENT_LABEL_KEYS } from "../../typing/constants/webhook.constant";
import type { WebhookEvent } from "../../typing/types/webhook.type";

interface Props {
  events: readonly WebhookEvent[];
}

export const WebhookEventList: FC<Props> = ({ events }) => {
  const { t } = useTranslation("integrations");

  if (events.length === WEBHOOK_EVENTS.length) {
    return (
      <DSText size="sm" component="span">
        {t("webhooks.allEvents")}
      </DSText>
    );
  }

  const labels = WEBHOOK_EVENTS.filter((event) => {
    return events.includes(event);
  }).map((event) => {
    return t(`events.${WEBHOOK_EVENT_LABEL_KEYS[event]}`);
  });

  return (
    <DSText size="sm" component="span">
      {labels.join(", ")}
    </DSText>
  );
};
