"use client";

import {
  DSActionIcon,
  DSAlert,
  DSBadge,
  DSButton,
  DSCard,
  DSErrorState,
  DSMenu,
  DSSkeleton,
  DSStack,
  DSTable,
  DSText,
  type DSMenuItem,
} from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetWebhooks } from "../../hooks/queries/use-get-webhooks";
import {
  MAX_WEBHOOKS_PER_PROJECT,
  WEBHOOK_LOADING_LINE_COUNT,
} from "../../typing/constants/webhook.constant";
import type { WebhookModalState } from "../../typing/types/webhook-modal-state.type";
import type { Webhook } from "../../typing/types/webhook.type";
import { DeleteWebhookModal } from "../delete-webhook-modal/delete-webhook-modal";
import { RotateWebhookSecretModal } from "../rotate-webhook-secret-modal/rotate-webhook-secret-modal";
import { WebhookDeliveriesDrawer } from "../webhook-deliveries-drawer/webhook-deliveries-drawer";
import { WebhookDeliveryStatusBadge } from "../webhook-delivery-status-badge/webhook-delivery-status-badge";
import { WebhookEventList } from "../webhook-event-list/webhook-event-list";
import { WebhookModal } from "../webhook-modal/webhook-modal";
import { WebhookSecretModal } from "../webhook-secret-modal/webhook-secret-modal";
import styles from "./webhooks-card.module.scss";

interface Props {
  projectKey: string;
}

export const WebhooksCard: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("integrations");
  const formatDate = useFormatDate();
  const { data: webhooks, isPending, isError, isFetching, refetch } = useGetWebhooks(projectKey);
  const [modalState, setModalState] = useState<WebhookModalState>({ mode: "closed" });
  const isLimitReached = (webhooks?.length ?? 0) >= MAX_WEBHOOKS_PER_PROJECT;

  const closeModal = (): void => {
    setModalState({ mode: "closed" });
  };

  const showSecret = (webhook: Webhook, secret: string): void => {
    setModalState({ mode: "secret", webhook, secret });
  };

  const buildMenuItems = (webhook: Webhook): DSMenuItem[] => {
    return [
      {
        key: "deliveries",
        label: t("webhooks.menu.deliveries"),
        icon: "webhook",
        onClick: () => {
          setModalState({ mode: "deliveries", webhook });
        },
      },
      {
        key: "edit",
        label: t("webhooks.menu.edit"),
        icon: "edit",
        onClick: () => {
          setModalState({ mode: "edit", webhook });
        },
      },
      {
        key: "rotate",
        label: t("webhooks.menu.rotate"),
        icon: "key",
        onClick: () => {
          setModalState({ mode: "rotate", webhook });
        },
      },
      { key: "divider", type: "divider" },
      {
        key: "delete",
        label: t("webhooks.menu.delete"),
        icon: "trash",
        isDanger: true,
        onClick: () => {
          setModalState({ mode: "delete", webhook });
        },
      },
    ];
  };

  const renderLastDelivery = (webhook: Webhook): ReactNode => {
    if (webhook.lastDelivery === null) {
      return <span className={styles.muted}>{t("webhooks.noDelivery")}</span>;
    }

    return (
      <div className={styles.stacked}>
        <WebhookDeliveryStatusBadge status={webhook.lastDelivery.status} />
        <DSText size="xs" color="muted" component="span">
          {formatDate(webhook.lastDelivery.lastAttemptAt ?? webhook.lastDelivery.createdAt)}
        </DSText>
      </div>
    );
  };

  const renderWebhooks = (): ReactNode => {
    if (isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("webhooks.loading")}>
          <DSSkeleton lineCount={WEBHOOK_LOADING_LINE_COUNT} />
        </div>
      );
    }

    if (isError || webhooks === undefined) {
      return (
        <DSErrorState
          title={t("webhooks.loadError")}
          retryLabel={t("webhooks.retry")}
          isRetrying={isFetching}
          titleOrder={3}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (webhooks.length === 0) {
      return <DSText color="muted">{t("webhooks.empty")}</DSText>;
    }

    return (
      <DSTable label={t("webhooks.tableLabel")}>
        <thead>
          <tr>
            <th scope="col">{t("webhooks.columns.url")}</th>
            <th scope="col">{t("webhooks.columns.events")}</th>
            <th scope="col">{t("webhooks.columns.status")}</th>
            <th scope="col">{t("webhooks.columns.lastDelivery")}</th>
            <th scope="col" className={styles.actionsCell}>
              <span className={styles.visuallyHidden}>{t("webhooks.columns.actions")}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {webhooks.map((webhook) => {
            return (
              <tr key={webhook.id}>
                <th scope="row" className={styles.urlCell}>
                  <span className={styles.url}>{webhook.url}</span>
                  {webhook.description !== null && (
                    <DSText size="xs" color="muted" component="span">
                      {webhook.description}
                    </DSText>
                  )}
                  <DSText size="xs" color="muted" component="span">
                    {t("webhooks.secretHint", { hint: webhook.secretHint })}
                  </DSText>
                </th>
                <td>
                  <WebhookEventList events={webhook.events} />
                </td>
                <td>
                  <DSBadge color={webhook.isActive ? "green" : "gray"}>
                    {webhook.isActive ? t("webhooks.active") : t("webhooks.inactive")}
                  </DSBadge>
                </td>
                <td>{renderLastDelivery(webhook)}</td>
                <td className={styles.actionsCell}>
                  <DSMenu
                    items={buildMenuItems(webhook)}
                    target={
                      <DSActionIcon
                        icon="dots"
                        ariaLabel={t("webhooks.actionsFor", { url: webhook.url })}
                      />
                    }
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </DSTable>
    );
  };

  return (
    <DSCard title={t("webhooks.title")}>
      <DSStack gap={4}>
        <div className={styles.header}>
          <DSText color="muted">{t("webhooks.description")}</DSText>
          <DSButton
            type="default"
            icon="plus"
            isDisabled={isPending || isLimitReached}
            onClick={() => {
              setModalState({ mode: "create" });
            }}
          >
            {t("webhooks.add")}
          </DSButton>
        </div>
        {isLimitReached && <DSAlert color="info">{t("errors.limitReached")}</DSAlert>}
        {renderWebhooks()}
      </DSStack>
      {(modalState.mode === "create" || modalState.mode === "edit") && (
        <WebhookModal
          projectKey={projectKey}
          webhook={modalState.mode === "edit" ? modalState.webhook : null}
          onClose={closeModal}
          onCreated={showSecret}
        />
      )}
      {modalState.mode === "secret" && (
        <WebhookSecretModal
          webhook={modalState.webhook}
          secret={modalState.secret}
          onClose={closeModal}
        />
      )}
      {modalState.mode === "rotate" && (
        <RotateWebhookSecretModal
          projectKey={projectKey}
          webhook={modalState.webhook}
          onClose={closeModal}
          onRotated={showSecret}
        />
      )}
      {modalState.mode === "delete" && (
        <DeleteWebhookModal
          projectKey={projectKey}
          webhook={modalState.webhook}
          onClose={closeModal}
        />
      )}
      {modalState.mode === "deliveries" && (
        <WebhookDeliveriesDrawer
          projectKey={projectKey}
          webhook={modalState.webhook}
          onClose={closeModal}
        />
      )}
    </DSCard>
  );
};
