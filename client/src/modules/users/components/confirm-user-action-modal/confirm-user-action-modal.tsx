"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostDeactivateUser } from "../../hooks/mutations/use-post-deactivate-user";
import { usePostReactivateUser } from "../../hooks/mutations/use-post-reactivate-user";
import { usePostResetUserTwoFactor } from "../../hooks/mutations/use-post-reset-user-two-factor";
import type { UserConfirmAction } from "../../typing/types/user-action.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";

interface Props {
  user: WorkspaceUser | null;
  action: UserConfirmAction | null;
  onClose: () => void;
}

export const ConfirmUserActionModal: FC<Props> = ({ user, action, onClose }) => {
  const { t } = useTranslation("users");
  const { showSuccessToast } = useShowToast();
  const deactivateUser = usePostDeactivateUser();
  const reactivateUser = usePostReactivateUser();
  const resetTwoFactor = usePostResetUserTwoFactor();
  const isPending =
    deactivateUser.isPending || reactivateUser.isPending || resetTwoFactor.isPending;

  if (user === null || action === null) {
    return null;
  }

  const name = user.name;

  const handleConfirm = (): void => {
    if (action === "deactivate") {
      deactivateUser.mutate(user.id, {
        onSuccess: () => {
          onClose();
          showSuccessToast(t("toasts.deactivated", { name }));
        },
      });
      return;
    }

    if (action === "resetTwoFactor") {
      resetTwoFactor.mutate(user.id, {
        onSuccess: () => {
          onClose();
          showSuccessToast(t("toasts.twoFactorReset", { name }));
        },
      });
      return;
    }

    reactivateUser.mutate(user.id, {
      onSuccess: (reactivatedUser) => {
        onClose();
        showSuccessToast(
          reactivatedUser.status === "invited"
            ? t("toasts.reactivatedInvited", { name })
            : t("toasts.reactivated", { name }),
        );
      },
    });
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t(`confirm.${action}.title`, { name })}
      isCloseDisabled={isPending}
      action={{
        label: t(`confirm.${action}.action`),
        type: action === "reactivate" ? "primary" : "danger",
        isLoading: isPending,
        onClick: handleConfirm,
      }}
    >
      <DSText>{t(`confirm.${action}.message`)}</DSText>
    </DSModal>
  );
};
