"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  caseCode: string;
  isOpened: boolean;
  isPending: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export const DeprecateTestCaseModal: FC<Props> = ({
  caseCode,
  isOpened,
  isPending,
  onConfirm,
  onClose,
}) => {
  const { t } = useTranslation("testCases");

  return (
    <DSModal
      isOpened={isOpened}
      onClose={onClose}
      title={t("deprecateConfirm.title", { code: caseCode })}
      isCloseDisabled={isPending}
      action={{
        label: t("actions.deprecate"),
        type: "danger",
        isLoading: isPending,
        onClick: onConfirm,
      }}
    >
      <DSText>{t("deprecateConfirm.message")}</DSText>
    </DSModal>
  );
};
