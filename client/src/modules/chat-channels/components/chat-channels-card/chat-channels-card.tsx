"use client";

import {
  DSActionIcon,
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
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePatchChatChannel } from "../../hooks/mutations/use-patch-chat-channel";
import { usePostChatChannelTest } from "../../hooks/mutations/use-post-chat-channel-test";
import { useGetChatChannels } from "../../hooks/queries/use-get-chat-channels";
import {
  CHAT_CHANNEL_EVENT_KEYS,
  MAX_CHAT_CHANNELS_PER_PROJECT,
} from "../../typing/constants/chat-channel.constant";
import type { ChatChannelModalState } from "../../typing/types/chat-channel-modal-state.type";
import type { ChatChannel } from "../../typing/types/chat-channel.type";
import { sortChatChannelEvents } from "../../utils/chat-channel-form.util";
import { ChatChannelDelivery } from "../chat-channel-delivery/chat-channel-delivery";
import { ChatChannelModal } from "../chat-channel-modal/chat-channel-modal";
import { DeleteChatChannelModal } from "../delete-chat-channel-modal/delete-chat-channel-modal";
import styles from "./chat-channels-card.module.scss";

interface Props {
  projectKey: string;
}

export const ChatChannelsCard: FC<Props> = ({ projectKey }) => {
  const { t } = useTranslation("chatChannels");
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const {
    data: chatChannels,
    isPending,
    isError,
    isFetching,
    refetch,
  } = useGetChatChannels(projectKey);
  const [modalState, setModalState] = useState<ChatChannelModalState>({ mode: "closed" });

  const showChannelError = (error: ApiError): void => {
    showErrorToast(error.code === "NOT_FOUND" ? t("errors.notFound") : resolveMessage(error));
  };

  const sendTest = usePostChatChannelTest(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (chatChannel) => {
      showSuccessToast(t("toasts.testSent", { name: chatChannel.name }));
    },
    onError: (error, chatChannelId) => {
      if (error.code === "CHAT_DELIVERY_FAILED") {
        const name = chatChannels?.find((candidate) => candidate.id === chatChannelId)?.name;
        showErrorToast(t("toasts.testFailed", { name }));
        return;
      }

      showChannelError(error);
    },
  });
  const toggleChannel = usePatchChatChannel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (chatChannel) => {
      showSuccessToast(
        t(chatChannel.isActive ? "toasts.turnedOn" : "toasts.turnedOff", {
          name: chatChannel.name,
        }),
      );
    },
    onError: showChannelError,
  });

  const closeModal = (): void => {
    setModalState({ mode: "closed" });
  };

  const isLimitReached = (chatChannels?.length ?? 0) >= MAX_CHAT_CHANNELS_PER_PROJECT;

  const buildMenuItems = (chatChannel: ChatChannel): DSMenuItem[] => {
    return [
      {
        key: "test",
        label: t("card.sendTest"),
        icon: "send",
        isDisabled: sendTest.isPending,
        onClick: () => {
          sendTest.mutate(chatChannel.id);
        },
      },
      {
        key: "edit",
        label: t("card.edit"),
        icon: "edit",
        onClick: () => {
          setModalState({ mode: "edit", chatChannel });
        },
      },
      {
        key: "toggle",
        label: chatChannel.isActive ? t("card.turnOff") : t("card.turnOn"),
        icon: chatChannel.isActive ? "close" : "check",
        isDisabled: toggleChannel.isPending,
        onClick: () => {
          toggleChannel.mutate({
            chatChannelId: chatChannel.id,
            body: { isActive: !chatChannel.isActive },
          });
        },
      },
      { key: "divider", type: "divider" },
      {
        key: "delete",
        label: t("card.delete"),
        icon: "trash",
        isDanger: true,
        onClick: () => {
          setModalState({ mode: "delete", chatChannel });
        },
      },
    ];
  };

  const renderEvents = (chatChannel: ChatChannel): string => {
    return sortChatChannelEvents(chatChannel.events)
      .map((event) => {
        return t(`events.${CHAT_CHANNEL_EVENT_KEYS[event]}`);
      })
      .join(", ");
  };

  const renderChannels = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true" aria-label={t("card.loading")}>
          <DSSkeleton lineCount={3} />
        </div>
      );
    }

    if (isError || chatChannels === undefined) {
      return (
        <DSErrorState
          title={t("card.loadError")}
          retryLabel={t("card.retry")}
          isRetrying={isFetching}
          titleOrder={3}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (chatChannels.length === 0) {
      return <DSText color="muted">{t("card.empty")}</DSText>;
    }

    return (
      <DSTable label={t("card.tableLabel")}>
        <caption className={styles.visuallyHidden}>{t("card.tableLabel")}</caption>
        <thead>
          <tr>
            <th scope="col">{t("card.channel")}</th>
            <th scope="col">{t("card.events")}</th>
            <th scope="col">{t("card.lastDelivery")}</th>
            <th scope="col" className={styles.actionsCell}>
              <span className={styles.visuallyHidden}>{t("card.actions")}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {chatChannels.map((chatChannel) => {
            return (
              <tr key={chatChannel.id}>
                <th scope="row" className={styles.channelCell}>
                  <div className={styles.channel}>
                    <div className={styles.channelName}>
                      <DSText size="sm" weight="medium" component="span">
                        {chatChannel.name}
                      </DSText>
                      <DSBadge color={chatChannel.kind === "slack" ? "violet" : "blue"}>
                        {t(`kinds.${chatChannel.kind}`)}
                      </DSBadge>
                      {!chatChannel.isActive && <DSBadge color="gray">{t("card.off")}</DSBadge>}
                    </div>
                    <DSText size="sm" color="muted" component="span" className={styles.url}>
                      {chatChannel.webhookUrlMasked}
                    </DSText>
                  </div>
                </th>
                <td className={styles.eventsCell}>
                  <DSText size="sm" component="span">
                    {renderEvents(chatChannel)}
                  </DSText>
                </td>
                <td className={styles.deliveryCell}>
                  <ChatChannelDelivery chatChannel={chatChannel} />
                </td>
                <td className={styles.actionsCell}>
                  <DSMenu
                    items={buildMenuItems(chatChannel)}
                    target={
                      <DSActionIcon
                        icon="dots"
                        ariaLabel={t("card.actionsFor", { name: chatChannel.name })}
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
    <DSCard title={t("card.title")}>
      <DSStack gap={4}>
        <div className={styles.header}>
          <DSText color="muted">{t("card.description")}</DSText>
          <DSButton
            type="default"
            icon="plus"
            isDisabled={isPending || isError || isLimitReached}
            onClick={() => {
              setModalState({ mode: "create" });
            }}
          >
            {t("card.add")}
          </DSButton>
        </div>
        {isLimitReached && (
          <DSText size="sm" color="muted">
            {t("card.limitReached", { max: MAX_CHAT_CHANNELS_PER_PROJECT })}
          </DSText>
        )}
        {renderChannels()}
      </DSStack>
      {(modalState.mode === "create" || modalState.mode === "edit") && (
        <ChatChannelModal
          projectKey={projectKey}
          chatChannel={modalState.mode === "edit" ? modalState.chatChannel : null}
          chatChannels={chatChannels ?? []}
          onClose={closeModal}
        />
      )}
      {modalState.mode === "delete" && (
        <DeleteChatChannelModal
          projectKey={projectKey}
          chatChannel={modalState.chatChannel}
          onClose={closeModal}
        />
      )}
    </DSCard>
  );
};
