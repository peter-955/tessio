"use client";

import { DSModal, DSText } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostGapReopen } from "../../hooks/mutations/use-post-gap-reopen";
import type { Gap } from "../../typing/types/gap.type";

interface Props {
  gap: Gap;
  onClose: () => void;
}

export const ReopenGapModal: FC<Props> = ({ gap, onClose }) => {
  const { t } = useTranslation("gaps");
  const { showSuccessToast } = useShowToast();
  const reopenGap = usePostGapReopen();

  const handleReopen = (): void => {
    reopenGap.mutate(
      { projectKey: gap.projectKey, gapId: gap.id },
      {
        onSuccess: () => {
          showSuccessToast(t("toasts.reopened"));
          onClose();
        },
        onError: (error: ApiError) => {
          if (error.code === "INVALID_STATUS_TRANSITION") {
            onClose();
          }
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("reopen.title")}
      isCloseDisabled={reopenGap.isPending}
      action={{
        label: t("reopen.submit"),
        icon: "restore",
        isLoading: reopenGap.isPending,
        onClick: handleReopen,
      }}
    >
      <DSText>{t("reopen.description")}</DSText>
    </DSModal>
  );
};
