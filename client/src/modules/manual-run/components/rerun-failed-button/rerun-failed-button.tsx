"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { ManualRunActionsRun } from "../../typing/types/manual-run-actions-run.type";
import type { RerunModalMode } from "../../typing/types/rerun-modal-mode.type";
import { RerunClaudeModal } from "../rerun-claude-modal/rerun-claude-modal";
import { RerunManualModal } from "../rerun-manual-modal/rerun-manual-modal";

interface Props {
  run: ManualRunActionsRun;
}

export const RerunFailedButton: FC<Props> = ({ run }) => {
  const { t } = useTranslation("manualRun");
  const project = useCurrentProject();
  const [mode, setMode] = useState<RerunModalMode | null>(null);
  const rerunCount = run.failedCount + run.blockedCount;
  const canRerunManually = checkHasProjectCapability(project, "run.record_manual");

  const handleClose = (): void => {
    setMode(null);
  };

  return (
    <>
      <DSButton
        icon="refresh"
        onClick={() => {
          setMode(run.executor === "claude" ? "claude" : "manual");
        }}
      >
        {t("rerun.action", { count: rerunCount })}
      </DSButton>
      {mode === "claude" && (
        <RerunClaudeModal
          runId={run.id}
          onClose={handleClose}
          onRerunManually={
            canRerunManually
              ? () => {
                  setMode("manual");
                }
              : undefined
          }
        />
      )}
      {mode === "manual" && (
        <RerunManualModal runId={run.id} rerunCount={rerunCount} onClose={handleClose} />
      )}
    </>
  );
};
