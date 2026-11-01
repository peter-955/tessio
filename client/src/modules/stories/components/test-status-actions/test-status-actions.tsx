"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutTestStatus } from "../../hooks/mutations/use-put-test-status";
import {
  TEST_STATUS_ACTION_ORDER,
  TEST_STATUS_ACTIONS,
} from "../../typing/constants/story.constant";
import type { StoryDetail } from "../../typing/types/story.type";
import type {
  ActionableTestStatus,
  SignOffTestStatus,
} from "../../typing/types/test-status-action.type";
import { checkIsSignOffStatus } from "../../utils/test-status.util";
import { ConfirmTestStatusModal } from "../confirm-test-status-modal/confirm-test-status-modal";

interface Props {
  story: StoryDetail;
}

export const TestStatusActions: FC<Props> = ({ story }) => {
  const { t } = useTranslation("stories");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const [confirmStatus, setConfirmStatus] = useState<SignOffTestStatus | null>(null);
  const putTestStatus = usePutTestStatus(project.key, story.jiraKey, {
    onSuccess: (updatedStory) => {
      setConfirmStatus(null);
      showSuccessToast(
        t("toasts.statusChanged", { status: t(`testStatuses.${updatedStory.testStatus}`) }),
      );
    },
    onError: () => {
      setConfirmStatus(null);
    },
  });
  const statuses = TEST_STATUS_ACTION_ORDER.filter((status) => {
    return story.availableTestStatuses.includes(status);
  });

  if (statuses.length === 0) {
    return null;
  }

  const handleClick = (status: ActionableTestStatus): void => {
    if (checkIsSignOffStatus(status)) {
      setConfirmStatus(status);

      return;
    }

    putTestStatus.mutate(status);
  };

  return (
    <>
      {statuses.map((status) => {
        const action = TEST_STATUS_ACTIONS[status];

        return (
          <DSButton
            key={status}
            type={action.buttonType}
            isLoading={putTestStatus.isPending && putTestStatus.variables === status}
            isDisabled={putTestStatus.isPending}
            onClick={() => {
              handleClick(status);
            }}
          >
            {t(`actions.${action.label}`)}
          </DSButton>
        );
      })}
      <ConfirmTestStatusModal
        jiraKey={story.jiraKey}
        status={confirmStatus}
        isPending={putTestStatus.isPending}
        onConfirm={(status) => {
          putTestStatus.mutate(status);
        }}
        onClose={() => {
          setConfirmStatus(null);
        }}
      />
    </>
  );
};
