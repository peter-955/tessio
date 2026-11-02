"use client";

import { DSAlert, DSModal, DSStack, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostPlanSignOff } from "../../hooks/mutations/use-post-plan-sign-off";
import type { PlanDetail } from "../../typing/types/plan.type";

interface Props {
  projectKey: string;
  plan: PlanDetail;
  onClose: () => void;
}

export const PlanSignOffModal: FC<Props> = ({ projectKey, plan, onClose }) => {
  const { t } = useTranslation("plans");
  const { showSuccessToast } = useShowToast();
  const signOff = usePostPlanSignOff(projectKey, plan.id, {
    onSuccess: () => {
      showSuccessToast(t("toasts.signedOff"));
      onClose();
    },
  });
  const failureCount = plan.progress.failures.length;
  const notRunCount = plan.progress.counts.notRun;
  const gapCount = plan.progress.gaps.length;
  const isBlocked = failureCount > 0;

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("signOff.title", { name: plan.name })}
      isCloseDisabled={signOff.isPending}
      action={{
        label: t("actions.signOff"),
        isLoading: signOff.isPending,
        isDisabled: isBlocked,
        onClick: () => {
          signOff.mutate();
        },
      }}
    >
      <DSStack gap={3}>
        {isBlocked ? (
          <DSAlert color="danger">{t("signOff.blocked", { count: failureCount })}</DSAlert>
        ) : (
          <DSText>{t("signOff.message")}</DSText>
        )}
        {!isBlocked && (notRunCount > 0 || gapCount > 0) && (
          <DSAlert color="warning">
            <DSStack gap={1}>
              {notRunCount > 0 && <span>{t("signOff.notRun", { count: notRunCount })}</span>}
              {gapCount > 0 && <span>{t("signOff.openGaps", { count: gapCount })}</span>}
            </DSStack>
          </DSAlert>
        )}
      </DSStack>
    </DSModal>
  );
};
