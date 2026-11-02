"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteStory } from "../../hooks/mutations/use-delete-story";
import type { StoryDetail } from "../../typing/types/story.type";

interface Props {
  projectKey: string;
  story: StoryDetail;
  onClose: () => void;
  onDeleted: () => void;
}

export const DeleteStoryModal: FC<Props> = ({ projectKey, story, onClose, onDeleted }) => {
  const { t } = useTranslation("stories");
  const { showSuccessToast } = useShowToast();
  const deleteStory = useDeleteStory(projectKey, story.jiraKey, {
    onSuccess: () => {
      showSuccessToast(t("editor.deleted", { key: story.jiraKey }));
      onClose();
      onDeleted();
    },
  });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("editor.deleteTitle", { key: story.jiraKey })}
      isCloseDisabled={deleteStory.isPending}
      action={{
        label: t("editor.delete"),
        type: "danger",
        icon: "trash",
        isLoading: deleteStory.isPending,
        onClick: () => {
          deleteStory.mutate();
        },
      }}
    >
      <DSText>{t("editor.deleteMessage")}</DSText>
    </DSModal>
  );
};
