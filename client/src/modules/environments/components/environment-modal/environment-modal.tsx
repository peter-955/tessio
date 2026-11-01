"use client";

import { DSInput, DSModal, DSStack, useDSForm } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostEnvironment } from "../../hooks/mutations/use-post-environment";
import { usePutEnvironment } from "../../hooks/mutations/use-put-environment";
import {
  MAX_ENVIRONMENT_NAME_LENGTH,
  MAX_ENVIRONMENT_URL_LENGTH,
} from "../../typing/constants/environment.constant";
import type { EnvironmentFormValues } from "../../typing/types/environment-form-values.type";
import type { Environment } from "../../typing/types/environment.type";
import {
  buildEnvironmentFormValues,
  buildEnvironmentRequest,
} from "../../utils/environment-request.util";
import { findEnvironmentUrlError } from "../../utils/environment-url.util";
import { toFormErrorText } from "../../utils/form-error.util";

interface Props {
  projectKey: string;
  environment: Environment | null;
  onClose: () => void;
}

export const EnvironmentModal: FC<Props> = ({ projectKey, environment, onClose }) => {
  const { t } = useTranslation("environments");
  const formId = useId();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const isEditing = environment !== null;

  const translateUrlError = (value: string): string | null => {
    const urlError = findEnvironmentUrlError(value);
    if (urlError === "tooLong") {
      return t("form.urlTooLong", { max: MAX_ENVIRONMENT_URL_LENGTH });
    }

    return urlError === "invalid" ? t("form.urlInvalid") : null;
  };

  const form = useDSForm<EnvironmentFormValues>({
    mode: "controlled",
    initialValues: buildEnvironmentFormValues(environment),
    validate: {
      name: (value) => {
        const name = value.trim();
        if (name === "") {
          return t("form.nameRequired");
        }

        return name.length > MAX_ENVIRONMENT_NAME_LENGTH
          ? t("form.nameTooLong", { max: MAX_ENVIRONMENT_NAME_LENGTH })
          : null;
      },
      baseUrl: translateUrlError,
      healthCheckUrl: (value) => {
        return value.trim() === "" ? null : translateUrlError(value);
      },
    },
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "ENVIRONMENT_NAME_ALREADY_USED") {
      form.setFieldError("name", t("errors.nameAlreadyUsed"));
      return;
    }

    showErrorToast(resolveMessage(error));
  };

  const createEnvironment = usePostEnvironment(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.created"));
      onClose();
    },
  });

  const updateEnvironment = usePutEnvironment(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });

  const isSubmitting = createEnvironment.isPending || updateEnvironment.isPending;

  const handleValidSubmit = (values: EnvironmentFormValues): void => {
    const body = buildEnvironmentRequest(values);

    if (environment === null) {
      createEnvironment.mutate(body);
      return;
    }

    updateEnvironment.mutate({ environmentId: environment.id, body });
  };

  const handleNameChange = (value: string): void => {
    form.setFieldValue("name", value);
  };

  const handleBaseUrlChange = (value: string): void => {
    form.setFieldValue("baseUrl", value);
  };

  const handleHealthCheckUrlChange = (value: string): void => {
    form.setFieldValue("healthCheckUrl", value);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={isEditing ? t("form.editTitle") : t("form.createTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: isEditing ? t("actions.save") : t("actions.create"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSInput
            label={t("form.name")}
            value={form.values.name}
            onChange={handleNameChange}
            error={toFormErrorText(form.errors.name)}
            isRequired
            isAutoFocused
          />
          <DSInput
            label={t("form.baseUrl")}
            value={form.values.baseUrl}
            onChange={handleBaseUrlChange}
            error={toFormErrorText(form.errors.baseUrl)}
            placeholder={t("form.baseUrlPlaceholder")}
            autoComplete="url"
            isRequired
          />
          <DSInput
            label={t("form.healthCheckUrl")}
            description={t("form.healthCheckHint")}
            value={form.values.healthCheckUrl}
            onChange={handleHealthCheckUrlChange}
            error={toFormErrorText(form.errors.healthCheckUrl)}
            placeholder={t("form.healthCheckUrlPlaceholder")}
            autoComplete="url"
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
