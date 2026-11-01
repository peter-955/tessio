"use client";

import { DSModal, DSStack, DSText } from "@/components/design-system";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteProjectMember } from "../../hooks/mutations/use-delete-project-member";

interface Props {
  projectKey: string;
  member: ProjectMember | null;
  isOpened: boolean;
  isSelf: boolean;
  onClose: () => void;
  onRemoved: (member: ProjectMember) => void;
}

export const RemoveMemberModal: FC<Props> = ({
  projectKey,
  member,
  isOpened,
  isSelf,
  onClose,
  onRemoved,
}) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const { mutate: deleteMember, isPending } = useDeleteProjectMember(projectKey);

  const handleConfirm = (): void => {
    if (member === null) {
      return;
    }

    deleteMember(member.userId, {
      onSuccess: () => {
        showSuccessToast(t("members.memberRemoved"));
        onClose();
        onRemoved(member);
      },
    });
  };

  return (
    <DSModal
      isOpened={isOpened && member !== null}
      onClose={onClose}
      title={t("members.removeTitle", { name: member?.name ?? "" })}
      isCloseDisabled={isPending}
      action={{
        label: t("members.removeConfirm"),
        type: "danger",
        icon: "trash",
        isLoading: isPending,
        onClick: handleConfirm,
      }}
    >
      <DSStack gap={2}>
        <DSText>{t("members.removeBody")}</DSText>
        {isSelf && <DSText weight="medium">{t("members.removeSelf")}</DSText>}
      </DSStack>
    </DSModal>
  );
};
