"use client";

import { DSInput, DSModal, DSStack, DSTextarea, useDSForm } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchSuite } from "../../hooks/mutations/use-patch-suite";
import { usePostSuite } from "../../hooks/mutations/use-post-suite";
import { useSuiteApiErrors } from "../../hooks/use-suite-api-errors";
import {
  MAX_SUITE_DESCRIPTION_LENGTH,
  MAX_SUITE_NAME_LENGTH,
} from "../../typing/constants/suite.constant";
import type { SuiteFormValues } from "../../typing/types/suite-form-values.type";
import type { SuiteDetail } from "../../typing/types/suite.type";
import { checkIsSuiteDescriptionTooLong, findSuiteNameError } from "../../utils/suite-form.util";
import {
  buildCreateSuiteRequest,
  buildSuiteFormValues,
  buildUpdateSuiteRequest,
} from "../../utils/suite-request.util";

interface Props {
  projectKey: string;
  suite: SuiteDetail | null;
  onClose: () => void;
  onCreated?: (suite: SuiteDetail) => void;
}

export const SuiteFormModal: FC<Props> = ({ projectKey, suite, onClose, onCreated }) => {
  const { t } = useTranslation("suites");
  const formId = useId();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSuiteApiErrors();
  const form = useDSForm<SuiteFormValues>({
    mode: "controlled",
    initialValues: buildSuiteFormValues(suite),
    validate: {
      name: (value) => {
        const error = findSuiteNameError(value);
        if (error === null) {
          return null;
        }

        return error === "required"
          ? t("form.nameRequired")
          : t("form.nameTooLong", { max: MAX_SUITE_NAME_LENGTH });
      },
      description: (value) => {
        return checkIsSuiteDescriptionTooLong(value)
          ? t("form.descriptionTooLong", { max: MAX_SUITE_DESCRIPTION_LENGTH })
          : null;
      },
    },
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "SUITE_NAME_ALREADY_USED") {
      form.setFieldError("name", t("errors.nameAlreadyUsed"));
      return;
    }

    showErrorToast(resolveMessage(error, apiErrors));
  };

  const createSuite = usePostSuite(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (createdSuite) => {
      showSuccessToast(t("toasts.created"));
      onCreated?.(createdSuite);
      onClose();
    },
  });
  const updateSuite = usePatchSuite(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });
  const isSubmitting = createSuite.isPending || updateSuite.isPending;

  const handleValidSubmit = (values: SuiteFormValues): void => {
    if (suite === null) {
      createSuite.mutate(buildCreateSuiteRequest(values));
      return;
    }

    const body = buildUpdateSuiteRequest(values, suite);
    if (Object.keys(body).length === 0) {
      onClose();
      return;
    }

    updateSuite.mutate({ suiteId: suite.id, body });
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={suite === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: suite === null ? t("form.create") : t("form.save"),
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
            error={
              typeof form.errors.description === "string" ? form.errors.description : undefined
            }
            minRows={3}
            isAutosize
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
