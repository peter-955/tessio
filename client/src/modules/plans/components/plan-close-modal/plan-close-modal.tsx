"use client";

import { DSModal, DSText } from "@/components/design-system";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostPlanClose } from "../../hooks/mutations/use-post-plan-close";
import type { PlanDetail } from "../../typing/types/plan.type";

interface Props {
  projectKey: string;
  plan: PlanDetail;
  onClose: () => void;
}

export const PlanCloseModal: FC<Props> = ({ projectKey, plan, onClose }) => {
  const { t } = useTranslation("plans");
  const { showSuccessToast } = useShowToast();
  const closePlan = usePostPlanClose(projectKey, plan.id, {
    onSuccess: () => {
      showSuccessToast(t("toasts.closed"));
      onClose();
    },
  });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("close.title", { name: plan.name })}
      isCloseDisabled={closePlan.isPending}
      action={{
        label: t("actions.close"),
        type: "danger",
        isLoading: closePlan.isPending,
        onClick: () => {
          closePlan.mutate();
        },
      }}
    >
      <DSText>
        {plan.status === "signed_off" ? t("close.messageSignedOff") : t("close.message")}
      </DSText>
    </DSModal>
  );
};
