"use client";

import {
  DSAlert,
  DSInput,
  DSModal,
  DSStack,
  DSStepEditor,
  DSText,
  type DSStepEditorLabels,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useReferenceSuggestions } from "@/modules/test-cases/hooks/use-reference-suggestions";
import type { TestFile } from "@/modules/test-cases/typing/types/test-case.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePatchSharedStep } from "../../hooks/mutations/use-patch-shared-step";
import { usePostSharedStep } from "../../hooks/mutations/use-post-shared-step";
import { useSharedStepApiErrors } from "../../hooks/use-shared-step-api-errors";
import {
  MAX_SHARED_STEP_ACTIONS,
  MAX_SHARED_STEP_KEY_LENGTH,
  MAX_SHARED_STEP_TEXT_LENGTH,
  MAX_SHARED_STEP_TITLE_LENGTH,
} from "../../typing/constants/shared-step.constant";
import type {
  SharedStepFormErrorKey,
  SharedStepFormErrors,
} from "../../typing/types/shared-step-form-errors.type";
import type { SharedStepFormValues } from "../../typing/types/shared-step-form-values.type";
import type { SharedStep } from "../../typing/types/shared-step.type";
import {
  buildCreateSharedStepRequest,
  buildSharedStepFormValues,
  buildUpdateSharedStepRequest,
  checkHasSharedStepChanges,
  checkHasSharedStepFormErrors,
  createEmptySharedStepFormValues,
  validateSharedStepForm,
} from "../../utils/shared-step-form.util";

const NO_FILES: TestFile[] = [];

interface Props {
  projectKey: string;
  sharedStep: SharedStep | null;
  onClose: () => void;
  onCreated?: (sharedStep: SharedStep) => void;
}

export const SharedStepFormModal: FC<Props> = ({ projectKey, sharedStep, onClose, onCreated }) => {
  const { t } = useTranslation("sharedSteps");
  const formId = useId();
  const { showSuccessToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const apiErrors = useSharedStepApiErrors();
  const suggestions = useReferenceSuggestions(projectKey, NO_FILES);
  const dataSuggestions = suggestions.filter((suggestion) => suggestion.kind === "data");
  const [values, setValues] = useState<SharedStepFormValues>(() => {
    return sharedStep === null
      ? createEmptySharedStepFormValues()
      : buildSharedStepFormValues(sharedStep);
  });
  const [errors, setErrors] = useState<SharedStepFormErrors | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [keyError, setKeyError] = useState<string | null>(null);

  const handleError = (error: ApiError): void => {
    if (error.code === "SHARED_STEP_KEY_ALREADY_USED") {
      setKeyError(t("errors.keyAlreadyUsed"));
      return;
    }

    setSubmitError(resolveMessage(error, apiErrors));
  };

  const createSharedStep = usePostSharedStep(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (createdStep) => {
      showSuccessToast(t("toasts.created", { title: createdStep.title }));
      onCreated?.(createdStep);
      onClose();
    },
  });
  const updateSharedStep = usePatchSharedStep(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (savedStep) => {
      showSuccessToast(t("toasts.saved", { title: savedStep.title }));
      onClose();
    },
  });
  const isSubmitting = createSharedStep.isPending || updateSharedStep.isPending;

  const translateError = (
    errorKey: SharedStepFormErrorKey | undefined,
    max: number,
  ): string | undefined => {
    return errorKey === undefined ? undefined : t(`form.errors.${errorKey}`, { max });
  };

  const changeValues = (nextValues: SharedStepFormValues): void => {
    setValues(nextValues);
    if (errors !== null) {
      setErrors(validateSharedStepForm(nextValues));
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const nextErrors = validateSharedStepForm(values);
    setErrors(nextErrors);
    setSubmitError(null);
    setKeyError(null);
    if (checkHasSharedStepFormErrors(nextErrors)) {
      return;
    }

    if (sharedStep === null) {
      createSharedStep.mutate(buildCreateSharedStepRequest(values));
      return;
    }

    const body = buildUpdateSharedStepRequest(values, sharedStep);
    if (!checkHasSharedStepChanges(body)) {
      onClose();
      return;
    }

    updateSharedStep.mutate({ key: sharedStep.key, body });
  };

  const stepLabels: DSStepEditorLabels = {
    step: (position) => t("form.step", { position }),
    action: t("form.action"),
    expected: t("form.expected"),
    addStep: t("form.addStep"),
    moveUp: t("form.moveUp"),
    moveDown: t("form.moveDown"),
    remove: t("form.removeStep"),
    stepActions: (position) => t("form.stepActions", { position }),
    suggestions: t("form.suggestions"),
    noSuggestions: t("form.noSuggestions"),
  };

  const stepErrors = Object.fromEntries(
    Object.entries(errors?.stepActions ?? {}).map(([stepId, errorKey]) => {
      return [stepId, translateError(errorKey, MAX_SHARED_STEP_TEXT_LENGTH) ?? ""];
    }),
  );

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={sharedStep === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: sharedStep === null ? t("form.create") : t("form.save"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={handleSubmit} noValidate>
        <DSStack gap={4}>
          {submitError !== null && <DSAlert color="danger">{submitError}</DSAlert>}
          <DSInput
            label={t("form.title")}
            value={values.title}
            onChange={(title) => {
              changeValues({ ...values, title: title.slice(0, MAX_SHARED_STEP_TITLE_LENGTH) });
            }}
            placeholder={t("form.titlePlaceholder")}
            error={translateError(errors?.title, MAX_SHARED_STEP_TITLE_LENGTH)}
            autoComplete="off"
            isRequired
            isAutoFocused
          />
          {sharedStep === null && (
            <DSInput
              label={t("form.key")}
              value={values.key}
              onChange={(key) => {
                setKeyError(null);
                changeValues({ ...values, key: key.slice(0, MAX_SHARED_STEP_KEY_LENGTH) });
              }}
              placeholder={t("form.keyPlaceholder")}
              description={t("form.keyDescription")}
              error={keyError ?? translateError(errors?.key, MAX_SHARED_STEP_KEY_LENGTH)}
              autoComplete="off"
              isRequired
            />
          )}
          <DSStack gap={2}>
            <DSText weight="medium">{t("form.steps")}</DSText>
            {errors?.steps !== undefined && (
              <DSText size="sm" color="danger">
                {translateError(errors.steps, MAX_SHARED_STEP_ACTIONS)}
              </DSText>
            )}
            <DSStepEditor
              steps={values.steps}
              onChange={(steps) => {
                changeValues({ ...values, steps });
              }}
              suggestions={dataSuggestions}
              labels={stepLabels}
              maxSteps={MAX_SHARED_STEP_ACTIONS}
              maxTextLength={MAX_SHARED_STEP_TEXT_LENGTH}
              errors={stepErrors}
              isDisabled={isSubmitting}
            />
          </DSStack>
        </DSStack>
      </form>
    </DSModal>
  );
};
