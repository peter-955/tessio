"use client";

import {
  DSAlert,
  DSCheckbox,
  DSInput,
  DSModal,
  DSStack,
  DSSwitch,
  DSText,
  useDSForm,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchWebhook } from "../../hooks/mutations/use-patch-webhook";
import { usePostWebhook } from "../../hooks/mutations/use-post-webhook";
import {
  MAX_WEBHOOK_DESCRIPTION_LENGTH,
  WEBHOOK_EVENTS,
  WEBHOOK_EVENT_LABEL_KEYS,
  WEBHOOK_URL_ERROR_KEYS,
} from "../../typing/constants/webhook.constant";
import type { WebhookFormValues } from "../../typing/types/webhook-form-values.type";
import type { Webhook } from "../../typing/types/webhook.type";
import {
  buildCreateWebhookRequest,
  buildUpdateWebhookRequest,
  buildWebhookFormValues,
  toggleWebhookEvent,
} from "../../utils/webhook-request.util";
import { findWebhookUrlError } from "../../utils/webhook-url.util";
import styles from "./webhook-modal.module.scss";

interface Props {
  projectKey: string;
  webhook: Webhook | null;
  onClose: () => void;
  onCreated: (webhook: Webhook, secret: string) => void;
}

export const WebhookModal: FC<Props> = ({ projectKey, webhook, onClose, onCreated }) => {
  const { t } = useTranslation("integrations");
  const formId = useId();
  const eventsDescriptionId = useId();
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const [serverError, setServerError] = useState<string | null>(null);
  const form = useDSForm<WebhookFormValues>({
    mode: "controlled",
    initialValues: buildWebhookFormValues(webhook),
    validate: {
      url: (value) => {
        const error = findWebhookUrlError(value);

        return error === null ? null : t(WEBHOOK_URL_ERROR_KEYS[error]);
      },
      description: (value) => {
        return value.trim().length > MAX_WEBHOOK_DESCRIPTION_LENGTH
          ? t("errors.descriptionTooLong")
          : null;
      },
      events: (value) => {
        return value.length === 0 ? t("errors.eventsRequired") : null;
      },
    },
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "WEBHOOK_URL_INVALID") {
      form.setFieldError("url", t("errors.urlInvalid"));
      return;
    }

    setServerError(
      resolveMessage(error, {
        CONFLICT: t("errors.limitReached"),
        NOT_FOUND: t("errors.notFound"),
      }),
    );
  };

  const createWebhook = usePostWebhook(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (response) => {
      showSuccessToast(t("toasts.created"));
      if (response.secret === null) {
        onClose();
        return;
      }

      onCreated(response.webhook, response.secret);
    },
  });
  const updateWebhook = usePatchWebhook(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });
  const isSubmitting = createWebhook.isPending || updateWebhook.isPending;

  const handleValidSubmit = (values: WebhookFormValues): void => {
    setServerError(null);
    if (webhook === null) {
      createWebhook.mutate(buildCreateWebhookRequest(values));
      return;
    }

    const body = buildUpdateWebhookRequest(values, webhook);
    if (Object.keys(body).length === 0) {
      onClose();
      return;
    }

    updateWebhook.mutate({ webhookId: webhook.id, body });
  };

  const eventsError = typeof form.errors.events === "string" ? form.errors.events : null;

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={webhook === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: webhook === null ? t("form.create") : t("form.save"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
          <DSInput
            label={t("form.url")}
            value={form.values.url}
            onChange={(value) => {
              form.setFieldValue("url", value);
            }}
            placeholder={t("form.urlPlaceholder")}
            description={t("form.urlDescription")}
            error={typeof form.errors.url === "string" ? form.errors.url : undefined}
            autoComplete="off"
            isRequired
            isAutoFocused
          />
          <DSInput
            label={t("form.description")}
            value={form.values.description}
            onChange={(value) => {
              form.setFieldValue("description", value);
            }}
            placeholder={t("form.descriptionPlaceholder")}
            error={
              typeof form.errors.description === "string" ? form.errors.description : undefined
            }
            autoComplete="off"
          />
          <fieldset className={styles.fieldset} aria-describedby={eventsDescriptionId}>
            <legend className={styles.legend}>{t("form.events")}</legend>
            <DSStack gap={2}>
              <DSText size="sm" color="muted" id={eventsDescriptionId}>
                {t("form.eventsDescription")}
              </DSText>
              <div className={styles.events}>
                {WEBHOOK_EVENTS.map((event) => {
                  return (
                    <DSCheckbox
                      key={event}
                      label={t(`events.${WEBHOOK_EVENT_LABEL_KEYS[event]}`)}
                      description={event}
                      isChecked={form.values.events.includes(event)}
                      onChange={(isChecked) => {
                        form.setFieldValue(
                          "events",
                          toggleWebhookEvent(form.values.events, event, isChecked),
                        );
                      }}
                    />
                  );
                })}
              </div>
              {eventsError !== null && (
                <DSText size="sm" color="danger" component="span">
                  {eventsError}
                </DSText>
              )}
            </DSStack>
          </fieldset>
          <DSSwitch
            label={t("form.isActive")}
            description={t("form.isActiveDescription")}
            isChecked={form.values.isActive}
            onChange={(isChecked) => {
              form.setFieldValue("isActive", isChecked);
            }}
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
