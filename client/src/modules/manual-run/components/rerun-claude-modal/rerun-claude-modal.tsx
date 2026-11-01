"use client";

import { DSButton, DSCode, DSModal, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildRerunCommand } from "../../utils/rerun-command.util";

interface Props {
  runId: string;
  onClose: () => void;
  onRerunManually?: () => void;
}

export const RerunClaudeModal: FC<Props> = ({ runId, onClose, onRerunManually }) => {
  const { t } = useTranslation("manualRun");

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("rerun.claudeTitle")}
      cancelLabel={t("rerun.close")}
    >
      <DSStack gap={4}>
        <DSText>{t("rerun.claudeDescription")}</DSText>
        <DSCode isBlock isCopyable>
          {buildRerunCommand(runId)}
        </DSCode>
        <DSText size="sm" color="muted">
          {t("rerun.claudeNote")}
        </DSText>
        {onRerunManually !== undefined && (
          <div>
            <DSButton type="ghost" icon="runs" onClick={onRerunManually}>
              {t("rerun.manualInstead")}
            </DSButton>
          </div>
        )}
      </DSStack>
    </DSModal>
  );
};
