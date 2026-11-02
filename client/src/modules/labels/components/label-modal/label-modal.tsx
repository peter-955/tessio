"use client";

import {
  DSInput,
  DSModal,
  DSSelect,
  DSStack,
  DSText,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchLabel } from "../../hooks/mutations/use-patch-label";
import { usePostLabel } from "../../hooks/mutations/use-post-label";
import { useLabelNameErrorText } from "../../hooks/use-label-name-error-text";
import { DEFAULT_LABEL_COLOR, LABEL_COLORS } from "../../typing/constants/label.constant";
import type { LabelFormValues } from "../../typing/types/label-form-values.type";
import type { Label, LabelColor } from "../../typing/types/label.type";
import { findLabelNameError } from "../../utils/label-name.util";
import {
  buildCreateLabelRequest,
  buildLabelFormValues,
  buildUpdateLabelRequest,
} from "../../utils/label-request.util";
import { LabelChip } from "../label-chip/label-chip";
import styles from "./label-modal.module.scss";

interface Props {
  projectKey: string;
  label: Label | null;
  labels: readonly Label[];
  onClose: () => void;
}

export const LabelModal: FC<Props> = ({ projectKey, label, labels, onClose }) => {
  const { t } = useTranslation("labels");
  const formId = useId();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const toNameErrorText = useLabelNameErrorText();
  const form = useDSForm<LabelFormValues>({
    mode: "controlled",
    initialValues: buildLabelFormValues(label),
    validate: {
      name: (value) => {
        return toNameErrorText(findLabelNameError(value, labels, label?.id ?? null));
      },
    },
  });
  const colorOptions = LABEL_COLORS.map((color): DSSelectOption<LabelColor> => {
    return { value: color, label: t(`colors.${color}`) };
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "CONFLICT") {
      form.setFieldError("name", t("errors.nameAlreadyUsed"));
      return;
    }

    showErrorToast(resolveMessage(error));
  };

  const createLabel = usePostLabel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.created"));
      onClose();
    },
  });
  const updateLabel = usePatchLabel(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: () => {
      showSuccessToast(t("toasts.updated"));
      onClose();
    },
  });
  const isSubmitting = createLabel.isPending || updateLabel.isPending;

  const handleValidSubmit = (values: LabelFormValues): void => {
    if (label === null) {
      createLabel.mutate(buildCreateLabelRequest(values));
      return;
    }

    const body = buildUpdateLabelRequest(values, label);
    if (Object.keys(body).length === 0) {
      onClose();
      return;
    }

    updateLabel.mutate({ labelId: label.id, body });
  };

  const previewName = form.values.name.trim();

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={label === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: label === null ? t("form.create") : t("form.save"),
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
          <DSSelect<LabelColor>
            label={t("form.color")}
            value={form.values.color}
            options={colorOptions}
            onChange={(color) => {
              form.setFieldValue("color", color ?? DEFAULT_LABEL_COLOR);
            }}
            isRequired
          />
          {previewName !== "" && (
            <div className={styles.preview}>
              <DSText size="sm" color="muted" component="span">
                {t("form.preview")}
              </DSText>
              <LabelChip name={previewName} color={form.values.color} />
            </div>
          )}
        </DSStack>
      </form>
    </DSModal>
  );
};
