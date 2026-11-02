"use client";

import {
  DSCheckbox,
  DSInput,
  DSModal,
  DSSelect,
  DSStack,
  DSSwitch,
  DSText,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchChatChannel } from "../../hooks/mutations/use-patch-chat-channel";
import { usePostChatChannel } from "../../hooks/mutations/use-post-chat-channel";
import {
  CHAT_CHANNEL_EVENT_KEYS,
  CHAT_CHANNEL_EVENTS,
  CHAT_CHANNEL_KINDS,
  DEFAULT_CHAT_CHANNEL_KIND,
  MAX_CHAT_CHANNEL_NAME_LENGTH,
  MAX_CHAT_WEBHOOK_URL_LENGTH,
} from "../../typing/constants/chat-channel.constant";
import type {
  ChatChannelEventsError,
  ChatChannelNameError,
  ChatWebhookUrlError,
} from "../../typing/types/chat-channel-form-error.type";
import type { ChatChannelFormValues } from "../../typing/types/chat-channel-form-values.type";
import type { ChatChannel, ChatChannelKind } from "../../typing/types/chat-channel.type";
import {
  buildChatChannelFormValues,
  buildCreateChatChannelRequest,
  buildUpdateChatChannelRequest,
  findChatChannelEventsError,
  findChatChannelNameError,
  findChatWebhookUrlError,
  toggleChatChannelEvent,
} from "../../utils/chat-channel-form.util";
import styles from "./chat-channel-modal.module.scss";

interface Props {
  projectKey: string;
  chatChannel: ChatChannel | null;
  chatChannels: readonly ChatChannel[];
  onClose: () => void;
}

export const ChatChannelModal: FC<Props> = ({ projectKey, chatChannel, chatChannels, onClose }) => {
  const { t } = useTranslation("chatChannels");
  const formId = useId();
  const eventsErrorId = useId();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const isCreating = chatChannel === null;

  const toMessage = (
    errorKey: ChatChannelNameError | ChatWebhookUrlError | ChatChannelEventsError | null,
    max?: number,
  ): string | null => {
    return errorKey === null ? null : t(`validation.${errorKey}`, { max });
  };

  const form = useDSForm<ChatChannelFormValues>({
    mode: "controlled",
    initialValues: buildChatChannelFormValues(chatChannel),
    validate: {
      name: (value) => {
        return toMessage(
          findChatChannelNameError(value, chatChannels, chatChannel?.id ?? null),
          MAX_CHAT_CHANNEL_NAME_LENGTH,
        );
      },
      webhookUrl: (value) => {
        return toMessage(findChatWebhookUrlError(value, isCreating), MAX_CHAT_WEBHOOK_URL_LENGTH);
      },
      events: (value) => {
        return toMessage(findChatChannelEventsError(value));
      },
    },
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "CONFLICT") {
      form.setFieldError("name", t("validation.nameAlreadyUsed"));
      return;
    }

    if (error.code === "WEBHOOK_URL_INVALID") {
      form.setFieldError("webhookUrl", t("errors.urlInvalid"));
      return;
    }

    if (error.code === "NOT_FOUND") {
      showErrorToast(t("errors.notFound"));
      return;
    }

    showErrorToast(resolveMessage(error));
  };

  const createChatChannel = usePostChatChannel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.created"));
      onClose();
    },
  });
  const updateChatChannel = usePatchChatChannel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });
  const isSubmitting = createChatChannel.isPending || updateChatChannel.isPending;

  const handleValidSubmit = (values: ChatChannelFormValues): void => {
    if (chatChannel === null) {
      createChatChannel.mutate(buildCreateChatChannelRequest(values));
      return;
    }

    const body = buildUpdateChatChannelRequest(values, chatChannel);
    if (Object.keys(body).length === 0) {
      onClose();
      return;
    }

    updateChatChannel.mutate({ chatChannelId: chatChannel.id, body });
  };

  const kindOptions = CHAT_CHANNEL_KINDS.map((kind): DSSelectOption<ChatChannelKind> => {
    return { value: kind, label: t(`kinds.${kind}`) };
  });
  const urlDescription = [
    t(`form.${form.values.kind}Help`),
    chatChannel === null
      ? t("form.secretNote")
      : t("form.savedUrl", { url: chatChannel.webhookUrlMasked }),
  ].join(" ");
  const eventsError = typeof form.errors.events === "string" ? form.errors.events : null;

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={isCreating ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: isCreating ? t("form.create") : t("form.save"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSSelect<ChatChannelKind>
            label={t("form.kind")}
            value={form.values.kind}
            options={kindOptions}
            onChange={(kind) => {
              form.setFieldValue("kind", kind ?? DEFAULT_CHAT_CHANNEL_KIND);
            }}
            isDisabled={!isCreating}
            isRequired
          />
          <DSInput
            label={t("form.name")}
            value={form.values.name}
            onChange={(value) => {
              form.setFieldValue("name", value);
            }}
            placeholder={t("form.namePlaceholder")}
            error={typeof form.errors.name === "string" ? form.errors.name : undefined}
            autoComplete="off"
            isRequired
            isAutoFocused
          />
          <DSInput
            label={isCreating ? t("form.webhookUrl") : t("form.newWebhookUrl")}
            value={form.values.webhookUrl}
            onChange={(value) => {
              form.setFieldValue("webhookUrl", value);
            }}
            placeholder={t("form.webhookUrlPlaceholder")}
            description={urlDescription}
            error={typeof form.errors.webhookUrl === "string" ? form.errors.webhookUrl : undefined}
            autoComplete="off"
            isRequired={isCreating}
          />
          <fieldset
            className={styles.events}
            aria-describedby={eventsError === null ? undefined : eventsErrorId}
          >
            <legend className={styles.legend}>
              <DSText size="sm" weight="medium" component="span">
                {t("form.events")}
              </DSText>
            </legend>
            <DSText size="sm" color="muted">
              {t("form.eventsDescription")}
            </DSText>
            <div className={styles.eventList}>
              {CHAT_CHANNEL_EVENTS.map((event) => {
                return (
                  <DSCheckbox
                    key={event}
                    label={t(`events.${CHAT_CHANNEL_EVENT_KEYS[event]}`)}
                    isChecked={form.values.events.includes(event)}
                    onChange={(isOn) => {
                      form.setFieldValue(
                        "events",
                        toggleChatChannelEvent(form.values.events, event, isOn),
                      );
                    }}
                  />
                );
              })}
            </div>
            {eventsError !== null && (
              <DSText size="sm" color="danger" id={eventsErrorId}>
                {eventsError}
              </DSText>
            )}
          </fieldset>
          <DSSwitch
            label={t("form.isActive")}
            isChecked={form.values.isActive}
            onChange={(isActive) => {
              form.setFieldValue("isActive", isActive);
            }}
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
