"use client";

import { DSModal, DSSelect } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { ApiError } from "@/lib/api/api-error";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useMemo, useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePutFailureAssignee } from "../../hooks/mutations/use-put-failure-assignee";
import { ASSIGN_FAILURE_FORM_ID, UNASSIGNED_OPTION } from "../../typing/constants/failure.constant";
import type { Failure } from "../../typing/types/failure.type";
import { buildAssignOptions } from "../../utils/assignee-options.util";

interface Props {
  failure: Pick<Failure, "id" | "assigneeId" | "testCaseCode">;
  onClose: () => void;
}

export const AssignFailureModal: FC<Props> = ({ failure, onClose }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const members = useGetProjectMembers(project.key);
  const assignFailure = usePutFailureAssignee(project.key, failure.id);
  const [selectedValue, setSelectedValue] = useState<string | null>(null);
  const [errorText, setErrorText] = useState<string | null>(null);
  const options = useMemo(() => {
    return buildAssignOptions(members.data ?? [], {
      unassigned: t("assign.unassigned"),
      formatRole: (role) => {
        return t(`roles.${role}`);
      },
    });
  }, [members.data, t]);
  const isCurrentAssigneeListed = options.some((option) => {
    return option.value === failure.assigneeId;
  });
  const initialValue =
    failure.assigneeId !== null && isCurrentAssigneeListed ? failure.assigneeId : UNASSIGNED_OPTION;
  const isSelectedValueListed = options.some((option) => {
    return option.value === selectedValue;
  });
  const value = selectedValue !== null && isSelectedValueListed ? selectedValue : initialValue;
  const nextAssigneeId = value === UNASSIGNED_OPTION ? null : value;
  const isUnchanged = nextAssigneeId === failure.assigneeId;

  const handleChange = (nextValue: string | null): void => {
    setSelectedValue(nextValue);
    setErrorText(null);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (isUnchanged || members.isPending) {
      return;
    }

    assignFailure.mutate(nextAssigneeId, {
      onSuccess: (updatedFailure) => {
        showSuccessToast(
          updatedFailure.assigneeName === null
            ? t("toasts.unassigned", { code: updatedFailure.testCaseCode })
            : t("toasts.assigned", {
                code: updatedFailure.testCaseCode,
                name: updatedFailure.assigneeName,
              }),
        );
        onClose();
      },
      onError: (error: ApiError) => {
        if (error.code === "ASSIGNEE_NOT_ACTIVE_MEMBER") {
          setErrorText(t("errors.assigneeNotActive"));
          void members.refetch();
        }

        if (error.code === "INVALID_STATUS_TRANSITION") {
          onClose();
        }
      },
    });
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("assign.title")}
      isCloseDisabled={assignFailure.isPending}
      action={{
        label: t("assign.submit"),
        icon: "user",
        formId: ASSIGN_FAILURE_FORM_ID,
        isLoading: assignFailure.isPending,
        isDisabled: isUnchanged || members.isPending,
      }}
    >
      <form id={ASSIGN_FAILURE_FORM_ID} onSubmit={handleSubmit} noValidate>
        <DSSelect<string>
          label={t("assign.label")}
          value={value}
          options={options}
          onChange={handleChange}
          error={errorText}
          isDisabled={members.isPending}
          isRequired
          isSearchable
        />
      </form>
    </DSModal>
  );
};
