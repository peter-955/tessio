"use client";

import {
  DSDateInput,
  DSInput,
  DSModal,
  DSSelect,
  DSStack,
  DSTextarea,
  useDSForm,
} from "@/components/design-system";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter } from "next/navigation";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchPlan } from "../../hooks/mutations/use-patch-plan";
import { usePostPlan } from "../../hooks/mutations/use-post-plan";
import {
  MAX_PLAN_DESCRIPTION_LENGTH,
  MAX_PLAN_NAME_LENGTH,
} from "../../typing/constants/plan.constant";
import type { PlanFormValues } from "../../typing/types/plan-form-values.type";
import type { PlanDetail } from "../../typing/types/plan.type";
import { buildEnvironmentOptions } from "../../utils/plan-environment-options.util";
import { buildPlanPath } from "../../utils/plan-path.util";
import {
  buildCreatePlanRequest,
  buildPlanFormValues,
  buildUpdatePlanRequest,
} from "../../utils/plan-request.util";

interface Props {
  projectKey: string;
  plan: PlanDetail | null;
  onClose: () => void;
}

export const PlanFormModal: FC<Props> = ({ projectKey, plan, onClose }) => {
  const { t } = useTranslation("plans");
  const formId = useId();
  const router = useRouter();
  const { showSuccessToast } = useShowToast();
  const environments = useGetEnvironments(projectKey);
  const form = useDSForm<PlanFormValues>({
    mode: "controlled",
    initialValues: buildPlanFormValues(plan),
    validate: {
      name: (value) => {
        const trimmedValue = value.trim();
        if (trimmedValue === "") {
          return t("form.nameRequired");
        }

        return trimmedValue.length > MAX_PLAN_NAME_LENGTH
          ? t("form.nameTooLong", { max: MAX_PLAN_NAME_LENGTH })
          : null;
      },
    },
  });
  const createPlan = usePostPlan(projectKey, {
    onSuccess: (createdPlan) => {
      showSuccessToast(t("toasts.created"));
      onClose();
      router.push(buildPlanPath(projectKey, createdPlan.id));
    },
  });
  const updatePlan = usePatchPlan(projectKey, plan?.id ?? "", {
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });
  const isSubmitting = createPlan.isPending || updatePlan.isPending;
  const options = buildEnvironmentOptions(environments.data ?? [], plan);

  const handleValidSubmit = (values: PlanFormValues): void => {
    if (plan === null) {
      createPlan.mutate(buildCreatePlanRequest(values));
      return;
    }

    const body = buildUpdatePlanRequest(values, plan);
    if (Object.keys(body).length === 0) {
      onClose();
      return;
    }

    updatePlan.mutate(body);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={plan === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: plan === null ? t("form.create") : t("form.save"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSInput
            label={t("form.name")}
            value={form.values.name}
            onChange={(value) => {
              form.setFieldValue("name", value);
            }}
            placeholder={t("form.namePlaceholder")}
            error={typeof form.errors.name === "string" ? form.errors.name : undefined}
            autoComplete="off"
            isRequired
            isAutoFocused
          />
          <DSTextarea
            label={t("form.description")}
            value={form.values.description}
            onChange={(value) => {
              form.setFieldValue("description", value);
            }}
            placeholder={t("form.descriptionPlaceholder")}
            maxLength={MAX_PLAN_DESCRIPTION_LENGTH}
            minRows={2}
          />
          <DSDateInput
            label={t("form.targetDate")}
            value={form.values.targetDate}
            onChange={(value) => {
              form.setFieldValue("targetDate", value);
            }}
          />
          <DSSelect<string>
            label={t("form.environment")}
            value={form.values.environmentId}
            options={options}
            onChange={(value) => {
              form.setFieldValue("environmentId", value);
            }}
            placeholder={t("form.environmentPlaceholder")}
            description={t("form.environmentDescription")}
            isClearable
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
