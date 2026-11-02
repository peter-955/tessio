"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteTestCaseQuarantine } from "../../hooks/mutations/use-delete-test-case-quarantine";
import { usePutTestCaseQuarantine } from "../../hooks/mutations/use-put-test-case-quarantine";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import { buildQuarantineRequest } from "../../utils/flaky-case.util";
import { QuarantineTestCaseModal } from "../quarantine-test-case-modal/quarantine-test-case-modal";

interface Props {
  detail: TestCaseDetail;
}

export const QuarantineAction: FC<Props> = ({ detail }) => {
  const { t } = useTranslation("flakyCases");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const [isModalOpened, setIsModalOpened] = useState(false);
  const [reason, setReason] = useState("");
  const quarantine = usePutTestCaseQuarantine(project.key, detail.code, {
    onSuccess: (updatedDetail) => {
      setIsModalOpened(false);
      setReason("");
      showSuccessToast(t("toasts.quarantined", { code: updatedDetail.code }));
    },
  });
  const release = useDeleteTestCaseQuarantine(project.key, detail.code, {
    onSuccess: (updatedDetail) => {
      showSuccessToast(t("toasts.released", { code: updatedDetail.code }));
    },
  });

  if (detail.isQuarantined) {
    return (
      <DSButton
        type="default"
        icon="quarantine"
        isLoading={release.isPending}
        onClick={() => {
          release.mutate();
        }}
      >
        {t("actions.release")}
      </DSButton>
    );
  }

  return (
    <>
      <DSButton
        type="default"
        icon="quarantine"
        onClick={() => {
          setIsModalOpened(true);
        }}
      >
        {t("actions.quarantine")}
      </DSButton>
      <QuarantineTestCaseModal
        caseCode={detail.code}
        isOpened={isModalOpened}
        isPending={quarantine.isPending}
        reason={reason}
        onReasonChange={setReason}
        onConfirm={() => {
          quarantine.mutate(buildQuarantineRequest(reason));
        }}
        onClose={() => {
          setIsModalOpened(false);
        }}
      />
    </>
  );
};
