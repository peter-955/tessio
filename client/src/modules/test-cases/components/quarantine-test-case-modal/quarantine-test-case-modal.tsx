"use client";

import { DSModal, DSText, DSTextarea } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MAX_QUARANTINE_REASON_LENGTH } from "../../typing/constants/flaky-case.constant";
import styles from "./quarantine-test-case-modal.module.scss";

interface Props {
  caseCode: string;
  isOpened: boolean;
  isPending: boolean;
  reason: string;
  onReasonChange: (reason: string) => void;
  onConfirm: () => void;
  onClose: () => void;
}

export const QuarantineTestCaseModal: FC<Props> = ({
  caseCode,
  isOpened,
  isPending,
  reason,
  onReasonChange,
  onConfirm,
  onClose,
}) => {
  const { t } = useTranslation("flakyCases");

  return (
    <DSModal
      isOpened={isOpened}
      onClose={onClose}
      title={t("modal.title", { code: caseCode })}
      isCloseDisabled={isPending}
      action={{
        label: t("actions.quarantine"),
        icon: "quarantine",
        isLoading: isPending,
        onClick: onConfirm,
      }}
    >
      <div className={styles.body}>
        <DSText>{t("modal.message")}</DSText>
        <DSTextarea
          label={t("modal.reason")}
          description={t("modal.reasonDescription")}
          placeholder={t("modal.reasonPlaceholder")}
          value={reason}
          onChange={onReasonChange}
          maxLength={MAX_QUARANTINE_REASON_LENGTH}
          isDisabled={isPending}
          minRows={2}
        />
      </div>
    </DSModal>
  );
};
