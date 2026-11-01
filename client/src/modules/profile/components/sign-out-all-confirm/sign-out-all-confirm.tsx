"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostSignOutAll } from "../../hooks/mutations/use-post-sign-out-all";

interface Props {
  isOpened: boolean;
  onClose: () => void;
}

export const SignOutAllConfirm: FC<Props> = ({ isOpened, onClose }) => {
  const { t } = useTranslation("profile");
  const { mutate: signOutAll, isPending, isSuccess } = usePostSignOutAll();
  const isLeaving = isPending || isSuccess;

  const handleConfirm = (): void => {
    signOutAll();
  };

  return (
    <DSModal
      isOpened={isOpened}
      onClose={onClose}
      title={t("signOutAll.title")}
      isCloseDisabled={isLeaving}
      action={{
        label: t("signOutAll.confirm"),
        type: "danger",
        isLoading: isLeaving,
        onClick: handleConfirm,
      }}
    >
      <DSText>{t("signOutAll.description")}</DSText>
    </DSModal>
  );
};
