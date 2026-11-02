"use client";

import { DSBadge, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ChatChannel } from "../../typing/types/chat-channel.type";
import styles from "./chat-channel-delivery.module.scss";

interface Props {
  chatChannel: ChatChannel;
}

export const ChatChannelDelivery: FC<Props> = ({ chatChannel }) => {
  const { t } = useTranslation("chatChannels");
  const formatDate = useFormatDate();
  const { lastDeliveryStatus, lastDeliveryAt, lastDeliveryError } = chatChannel;

  if (lastDeliveryStatus === null) {
    return (
      <DSText size="sm" color="muted" component="span">
        {t("delivery.none")}
      </DSText>
    );
  }

  return (
    <div className={styles.delivery}>
      <div className={styles.status}>
        <DSBadge color={lastDeliveryStatus === "delivered" ? "green" : "red"}>
          {t(`delivery.${lastDeliveryStatus}`)}
        </DSBadge>
        {lastDeliveryAt !== null && (
          <DSText size="sm" color="muted" component="span">
            {formatDate(lastDeliveryAt)}
          </DSText>
        )}
      </div>
      {lastDeliveryStatus === "failed" && lastDeliveryError !== null && (
        <DSText size="sm" color="danger" component="span" className={styles.error}>
          {lastDeliveryError}
        </DSText>
      )}
    </div>
  );
};
