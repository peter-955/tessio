"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  name: string;
  isArchiving: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export const ArchiveSuiteModal: FC<Props> = ({ name, isArchiving, onConfirm, onClose }) => {
  const { t } = useTranslation("suites");

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("archive.title")}
      isCloseDisabled={isArchiving}
      action={{
        label: t("archive.confirm"),
        icon: "archive",
        type: "danger",
        isLoading: isArchiving,
        onClick: onConfirm,
      }}
    >
      <DSText>{t("archive.description", { name })}</DSText>
    </DSModal>
  );
};
