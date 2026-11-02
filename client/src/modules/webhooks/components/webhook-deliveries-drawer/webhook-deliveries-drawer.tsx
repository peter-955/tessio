"use client";

import {
  DSActionIcon,
  DSButton,
  DSCode,
  DSDrawer,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSTable,
  DSText,
} from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { Fragment, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePostWebhookRedelivery } from "../../hooks/mutations/use-post-webhook-redelivery";
import { useGetWebhookDeliveries } from "../../hooks/queries/use-get-webhook-deliveries";
import {
  WEBHOOK_EVENT_LABEL_KEYS,
  WEBHOOK_LOADING_LINE_COUNT,
} from "../../typing/constants/webhook.constant";
import type { Webhook, WebhookDelivery } from "../../typing/types/webhook.type";
import { WebhookDeliveryStatusBadge } from "../webhook-delivery-status-badge/webhook-delivery-status-badge";
import styles from "./webhook-deliveries-drawer.module.scss";

const PAYLOAD_INDENT = 2;

const COLUMN_COUNT = 6;

interface Props {
  projectKey: string;
  webhook: Webhook;
  onClose: () => void;
}

export const WebhookDeliveriesDrawer: FC<Props> = ({ projectKey, webhook, onClose }) => {
  const { t } = useTranslation("integrations");
  const formatDate = useFormatDate();
  const { showSuccessToast } = useShowToast();
  const [openedPayloadId, setOpenedPayloadId] = useState<string | null>(null);
  const { data, isPending, isError, isFetching, refetch } = useGetWebhookDeliveries(
    projectKey,
    webhook.id,
  );
  const redeliver = usePostWebhookRedelivery(projectKey, {
    onSuccess: () => {
      showSuccessToast(t("toasts.redelivered"));
    },
  });

  const renderAnswer = (delivery: WebhookDelivery): ReactNode => {
    return (
      <div className={styles.answer}>
        <span>{delivery.responseStatus ?? t("deliveries.noResponse")}</span>
        {delivery.error !== null && (
          <DSText size="xs" color="danger" component="span" className={styles.error}>
            {delivery.error}
          </DSText>
        )}
      </div>
    );
  };

  const renderDeliveryRows = (delivery: WebhookDelivery): ReactNode => {
    const eventLabel = t(`events.${WEBHOOK_EVENT_LABEL_KEYS[delivery.event]}`);
    const sentAt = formatDate(delivery.lastAttemptAt ?? delivery.createdAt);
    const isPayloadOpened = openedPayloadId === delivery.id;
    const isRedelivering = redeliver.isPending && redeliver.variables.deliveryId === delivery.id;

    return (
      <Fragment key={delivery.id}>
        <tr>
          <th scope="row" className={styles.eventCell}>
            <span>{eventLabel}</span>
            {delivery.redeliveryOfId !== null && (
              <DSText size="xs" color="muted" component="span">
                {t("deliveries.redelivery")}
              </DSText>
            )}
          </th>
          <td>
            <WebhookDeliveryStatusBadge status={delivery.status} />
          </td>
          <td className={styles.muted}>{t("deliveries.attempts", { count: delivery.attempts })}</td>
          <td>{renderAnswer(delivery)}</td>
          <td className={styles.muted}>{sentAt}</td>
          <td className={styles.actionsCell}>
            <div className={styles.actions}>
              <DSActionIcon
                icon={isPayloadOpened ? "eyeOff" : "eye"}
                ariaLabel={
                  isPayloadOpened
                    ? t("deliveries.hidePayload", { event: eventLabel, time: sentAt })
                    : t("deliveries.showPayload", { event: eventLabel, time: sentAt })
                }
                aria-expanded={isPayloadOpened}
                onClick={() => {
                  setOpenedPayloadId(isPayloadOpened ? null : delivery.id);
                }}
              />
              <DSButton
                type="default"
                icon="refresh"
                isLoading={isRedelivering}
                isDisabled={redeliver.isPending && !isRedelivering}
                ariaLabel={t("deliveries.redeliverLabel", { event: eventLabel, time: sentAt })}
                onClick={() => {
                  redeliver.mutate({ webhookId: webhook.id, deliveryId: delivery.id });
                }}
              >
                {t("deliveries.redeliver")}
              </DSButton>
            </div>
          </td>
        </tr>
        {isPayloadOpened && (
          <tr>
            <td colSpan={COLUMN_COUNT} className={styles.payloadCell}>
              <DSCode isBlock isCopyable>
                {JSON.stringify(delivery.payload, null, PAYLOAD_INDENT)}
              </DSCode>
            </td>
          </tr>
        )}
      </Fragment>
    );
  };

  const renderContent = (): ReactNode => {
    if (isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("deliveries.loading")}>
          <DSSkeleton lineCount={WEBHOOK_LOADING_LINE_COUNT} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("deliveries.loadError")}
          retryLabel={t("webhooks.retry")}
          isRetrying={isFetching}
          titleOrder={3}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.length === 0) {
      return <DSEmptyState title={t("deliveries.empty")} icon="webhook" size="sm" />;
    }

    return (
      <DSTable label={t("deliveries.tableLabel")}>
        <thead>
          <tr>
            <th scope="col">{t("deliveries.columns.event")}</th>
            <th scope="col">{t("deliveries.columns.status")}</th>
            <th scope="col">{t("deliveries.columns.attempts")}</th>
            <th scope="col">{t("deliveries.columns.response")}</th>
            <th scope="col">{t("deliveries.columns.time")}</th>
            <th scope="col" className={styles.actionsCell}>
              <span className={styles.visuallyHidden}>{t("deliveries.columns.actions")}</span>
            </th>
          </tr>
        </thead>
        <tbody>{data.map(renderDeliveryRows)}</tbody>
      </DSTable>
    );
  };

  return (
    <DSDrawer
      isOpened
      onClose={onClose}
      title={t("deliveries.title")}
      size="lg"
      closeLabel={t("deliveries.close")}
    >
      <DSStack gap={4}>
        <DSStack gap={1}>
          <DSText weight="medium" className={styles.url}>
            {webhook.url}
          </DSText>
          <DSText size="sm" color="muted">
            {t("deliveries.description")}
          </DSText>
        </DSStack>
        {renderContent()}
      </DSStack>
    </DSDrawer>
  );
};
