"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostArchiveProject } from "../../hooks/mutations/use-post-archive-project";
import { usePostUnarchiveProject } from "../../hooks/mutations/use-post-unarchive-project";
import type { ArchiveTarget } from "../../typing/types/archive-target.type";

interface Props {
  target: ArchiveTarget | null;
  isOpened: boolean;
  onClose: () => void;
}

export const ArchiveProjectModal: FC<Props> = ({ target, isOpened, onClose }) => {
  const { t } = useTranslation("projects");
  const { showSuccessToast } = useShowToast();
  const { mutate: archiveProject, isPending: isArchiving } = usePostArchiveProject();
  const { mutate: unarchiveProject, isPending: isUnarchiving } = usePostUnarchiveProject();
  const isPending = isArchiving || isUnarchiving;
  const mode = target?.mode ?? "archive";
  const projectName = target?.project.name ?? "";

  const handleConfirm = (): void => {
    if (target === null) {
      return;
    }

    const handleSuccess = (): void => {
      showSuccessToast(t(`${mode}.success`));
      onClose();
    };

    if (mode === "archive") {
      archiveProject(target.project.key, { onSuccess: handleSuccess });
      return;
    }

    unarchiveProject(target.project.key, { onSuccess: handleSuccess });
  };

  return (
    <DSModal
      isOpened={isOpened && target !== null}
      onClose={onClose}
      title={t(`${mode}.title`, { name: projectName })}
      isCloseDisabled={isPending}
      action={{
        label: t(`${mode}.confirm`),
        type: mode === "archive" ? "danger" : "primary",
        icon: mode === "archive" ? "archive" : "restore",
        isLoading: isPending,
        onClick: handleConfirm,
      }}
    >
      <DSText>{t(`${mode}.body`)}</DSText>
    </DSModal>
  );
};
