"use client";

import {
  DSModal,
  DSSelect,
  DSStack,
  DSTextarea,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { SUSPECTED_CAUSES } from "@/shared/typing/constants/suspected-cause.constant";
import type { SuspectedCause } from "@/shared/typing/types/test-run.type";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutFailureCause } from "../../../hooks/mutations/use-put-failure-cause";
import { MAX_CAUSE_REASON_LENGTH } from "../../../typing/constants/failure.constant";
import type { Failure } from "../../../typing/types/failure.type";

interface Props {
  failure: Pick<Failure, "id" | "cause" | "causeReason" | "testCaseCode">;
  onClose: () => void;
}

export const ChangeCauseModal: FC<Props> = ({ failure, onClose }) => {
  const { t } = useTranslation("failures");
  const { t: translateDiagnosis } = useTranslation("diagnosis");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const changeCause = usePutFailureCause(project.key, failure.id);
  const [cause, setCause] = useState<SuspectedCause | null>(failure.cause);
  const [reason, setReason] = useState(failure.causeReason ?? "");
  const options = SUSPECTED_CAUSES.map((value): DSSelectOption<SuspectedCause> => {
    return { value, label: translateDiagnosis(`cause.${value}`) };
  });

  const handleSave = (): void => {
    if (cause === null) {
      return;
    }

    changeCause.mutate(
      { cause, reason: reason.trim() === "" ? null : reason },
      {
        onSuccess: () => {
          showSuccessToast(t("toasts.causeChanged", { code: failure.testCaseCode }));
          onClose();
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("cause.modalTitle")}
      isCloseDisabled={changeCause.isPending}
      action={{
        label: t("cause.save"),
        icon: "check",
        isLoading: changeCause.isPending,
        isDisabled: cause === null,
        onClick: handleSave,
      }}
    >
      <DSStack gap={4}>
        <DSSelect<SuspectedCause>
          label={translateDiagnosis("suspectedCause")}
          value={cause}
          options={options}
          onChange={setCause}
          isRequired
        />
        <DSTextarea
          label={t("cause.reason")}
          value={reason}
          onChange={setReason}
          maxLength={MAX_CAUSE_REASON_LENGTH}
          minRows={2}
          isAutosize
        />
      </DSStack>
    </DSModal>
  );
};
