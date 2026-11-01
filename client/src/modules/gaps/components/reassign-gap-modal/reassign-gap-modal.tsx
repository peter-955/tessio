"use client";

import { DSModal, DSSelect } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useMemo, useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePutGapAssignee } from "../../hooks/mutations/use-put-gap-assignee";
import { REASSIGN_GAP_FORM_ID } from "../../typing/constants/gap.constant";
import type { Gap } from "../../typing/types/gap.type";
import {
  buildAssigneeChoiceValue,
  buildAssigneeOptions,
  buildReassignBody,
  parseAssigneeChoice,
} from "../../utils/assignee-options.util";

interface Props {
  gap: Gap;
  onClose: () => void;
}

export const ReassignGapModal: FC<Props> = ({ gap, onClose }) => {
  const { t } = useTranslation("gaps");
  const { showSuccessToast } = useShowToast();
  const members = useGetProjectMembers(gap.projectKey);
  const reassignGap = usePutGapAssignee();
  const [value, setValue] = useState<string | null>(() => {
    return buildAssigneeChoiceValue(gap);
  });
  const [errorText, setErrorText] = useState<string | null>(null);
  const options = useMemo(() => {
    return buildAssigneeOptions(members.data ?? [], {
      formatRole: (role) => {
        return t(`roles.${role}`);
      },
      formatAnyRole: (role) => {
        return t("reassign.anyRole", { role: t(`roles.${role}`) });
      },
    });
  }, [members.data, t]);
  const isValueListed = options.some((option) => {
    return option.value === value;
  });
  const choice = isValueListed ? parseAssigneeChoice(value) : null;

  const handleChange = (nextValue: string | null): void => {
    setValue(nextValue);
    setErrorText(null);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (choice === null) {
      return;
    }

    reassignGap.mutate(
      { projectKey: gap.projectKey, gapId: gap.id, body: buildReassignBody(choice) },
      {
        onSuccess: () => {
          showSuccessToast(t("toasts.reassigned"));
          onClose();
        },
        onError: (error: ApiError) => {
          if (error.code === "ASSIGNEE_NOT_ACTIVE_MEMBER") {
            setErrorText(t("errors.assigneeNotActive"));
            void members.refetch();
          }

          if (error.code === "GAP_NOT_OPEN") {
            onClose();
          }
        },
      },
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("reassign.title")}
      isCloseDisabled={reassignGap.isPending}
      action={{
        label: t("reassign.submit"),
        icon: "members",
        formId: REASSIGN_GAP_FORM_ID,
        isLoading: reassignGap.isPending,
        isDisabled: choice === null,
      }}
    >
      <form id={REASSIGN_GAP_FORM_ID} onSubmit={handleSubmit} noValidate>
        <DSSelect<string>
          label={t("reassign.label")}
          value={isValueListed ? value : null}
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
