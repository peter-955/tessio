"use client";

import { DSAlert, DSModal, DSStack, DSText } from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteChatChannel } from "../../hooks/mutations/use-delete-chat-channel";
import type { ChatChannel } from "../../typing/types/chat-channel.type";

interface Props {
  projectKey: string;
  chatChannel: ChatChannel;
  onClose: () => void;
}

export const DeleteChatChannelModal: FC<Props> = ({ projectKey, chatChannel, onClose }) => {
  const { t } = useTranslation("chatChannels");
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const deleteChatChannel = useDeleteChatChannel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      showSuccessToast(t("toasts.deleted"));
      onClose();
    },
  });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("delete.title")}
      isCloseDisabled={deleteChatChannel.isPending}
      action={{
        label: t("delete.confirm"),
        type: "danger",
        icon: "trash",
        isLoading: deleteChatChannel.isPending,
        onClick: () => {
          deleteChatChannel.mutate(chatChannel.id);
        },
      }}
    >
      <DSStack gap={3}>
        <DSText>{t("delete.message", { name: chatChannel.name })}</DSText>
        {deleteChatChannel.error !== null && (
          <DSAlert color="danger">
            {deleteChatChannel.error.code === "NOT_FOUND"
              ? t("errors.notFound")
              : resolveMessage(deleteChatChannel.error)}
          </DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
