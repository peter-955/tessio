"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_STATUS_ACTIONS } from "../../typing/constants/story.constant";
import type { SignOffTestStatus } from "../../typing/types/test-status-action.type";

interface Props {
  jiraKey: string;
  status: SignOffTestStatus | null;
  isPending: boolean;
  onConfirm: (status: SignOffTestStatus) => void;
  onClose: () => void;
}

export const ConfirmTestStatusModal: FC<Props> = ({
  jiraKey,
  status,
  isPending,
  onConfirm,
  onClose,
}) => {
  const { t } = useTranslation("stories");

  if (status === null) {
    return null;
  }

  const action = TEST_STATUS_ACTIONS[status];

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t(`confirm.${status}.title`, { jiraKey })}
      isCloseDisabled={isPending}
      action={{
        label: t(`actions.${action.label}`),
        type: action.buttonType === "danger" ? "danger" : "primary",
        isLoading: isPending,
        onClick: () => {
          onConfirm(status);
        },
      }}
    >
      <DSText>{t(`confirm.${status}.message`)}</DSText>
    </DSModal>
  );
};
