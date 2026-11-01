"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutFailureStatus } from "../../hooks/mutations/use-put-failure-status";
import type { Failure } from "../../typing/types/failure.type";
import { buildFailureStatusActions } from "../../utils/failure-actions.util";

interface Props {
  failure: Pick<Failure, "id" | "status" | "testCaseCode">;
}

export const FailureStatusActions: FC<Props> = ({ failure }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const changeStatus = usePutFailureStatus(project.key, failure.id);
  const actions = buildFailureStatusActions(failure.status, project);

  const handleClick = (status: Failure["status"]): void => {
    changeStatus.mutate(status, {
      onSuccess: (updatedFailure) => {
        showSuccessToast(
          t("toasts.statusChanged", {
            code: updatedFailure.testCaseCode,
            status: t(`status.${updatedFailure.status}`),
          }),
        );
      },
    });
  };

  return (
    <>
      {actions.map((action) => {
        return (
          <DSButton
            key={action.status}
            type={action.type}
            isLoading={changeStatus.isPending && changeStatus.variables === action.status}
            isDisabled={changeStatus.isPending}
            onClick={() => {
              handleClick(action.status);
            }}
          >
            {t(`actions.${action.labelKey}`)}
          </DSButton>
        );
      })}
    </>
  );
};
