"use client";

import { DSAlert, DSModal, DSStack, DSTextarea } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostManualRunFinish } from "../../hooks/mutations/use-post-manual-run-finish";
import { useManualRunApiErrors } from "../../hooks/use-manual-run-api-errors";
import { MAX_SUMMARY_LENGTH } from "../../typing/constants/manual-run.constant";
import type { ManualRun } from "../../typing/types/manual-run.type";
import { buildRunDetailPath } from "../../utils/manual-run-path.util";
import { countRecordedCases } from "../../utils/run-case.util";

interface Props {
  run: ManualRun;
  onClose: () => void;
}

export const FinishRunModal: FC<Props> = ({ run, onClose }) => {
  const { t } = useTranslation("manualRun");
  const router = useRouter();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useManualRunApiErrors();
  const { showSuccessToast } = useShowToast();
  const [summary, setSummary] = useState("");
  const finishRun = usePostManualRunFinish(project.key, run.id);
  const recordedCount = countRecordedCases(run.cases);
  const unrecordedCount = run.cases.length - recordedCount;

  const handleConfirm = (): void => {
    const trimmedSummary = summary.trim();

    finishRun.mutate(
      { summary: trimmedSummary === "" ? null : trimmedSummary },
      {
        onSuccess: () => {
          showSuccessToast(t("finish.finished"));
          router.push(buildRunDetailPath(project.key, run.id));
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("finish.title")}
      isCloseDisabled={finishRun.isPending}
      action={{
        label: t("finish.confirm"),
        type: recordedCount === 0 ? "danger" : "primary",
        isLoading: finishRun.isPending,
        onClick: handleConfirm,
      }}
    >
      <DSStack gap={4}>
        {recordedCount === 0 ? (
          <DSAlert color="danger">{t("finish.noResults")}</DSAlert>
        ) : (
          unrecordedCount > 0 && (
            <DSAlert color="warning">{t("finish.unrecorded", { count: unrecordedCount })}</DSAlert>
          )
        )}
        <DSTextarea
          label={t("finish.summary")}
          value={summary}
          onChange={setSummary}
          maxLength={MAX_SUMMARY_LENGTH}
          isDisabled={finishRun.isPending}
        />
        {finishRun.error !== null && (
          <DSAlert color="danger">{resolveMessage(finishRun.error, apiErrors)}</DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
