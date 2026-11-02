"use client";

import {
  DSCheckbox,
  DSInput,
  DSModal,
  DSPasswordInput,
  DSSelect,
  DSStack,
  DSTextarea,
  useDSForm,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostDataItem } from "../../hooks/mutations/use-post-data-item";
import { usePutDataItem } from "../../hooks/mutations/use-put-data-item";
import {
  DATA_ITEM_KEY_PATTERN,
  MAX_DATA_ITEM_DESCRIPTION_LENGTH,
  MAX_DATA_ITEM_VALUE_LENGTH,
  PROJECT_SCOPE_ID,
} from "../../typing/constants/test-data.constant";
import type { DataItemFormValues } from "../../typing/types/data-item-form-values.type";
import type { DataItemModalState } from "../../typing/types/data-item-modal-state.type";
import type { DataItem } from "../../typing/types/data-item.type";
import type { Environment } from "../../typing/types/environment.type";
import {
  buildCreateDataItemRequest,
  buildDataItemFormValues,
  buildUpdateDataItemRequest,
  isKeepingSecretValue,
} from "../../utils/data-item-form.util";
import { toFormErrorText } from "../../utils/form-error.util";

interface Props {
  projectKey: string;
  state: DataItemModalState;
  environments: readonly Environment[];
  onClose: () => void;
  onSaved?: (item: DataItem) => void;
}

export const DataItemModal: FC<Props> = ({ projectKey, state, environments, onClose, onSaved }) => {
  const { t } = useTranslation("testData");
  const formId = useId();
  const project = useCurrentProject();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const canEditSecrets = checkHasProjectCapability(project, "secret.edit");
  const editingItem = state.mode === "edit" ? state.item : null;
  const isFromCell = state.mode === "create" && state.preset !== null;
  const isScopeLocked = editingItem !== null || isFromCell;

  const form = useDSForm<DataItemFormValues>({
    mode: "controlled",
    initialValues: buildDataItemFormValues(state),
    validate: {
      key: (value) => {
        return DATA_ITEM_KEY_PATTERN.test(value.trim()) ? null : t("form.keyInvalid");
      },
      value: (value, values) => {
        if (value === "") {
          return isKeepingSecretValue(editingItem, values.kind) ? null : t("form.valueRequired");
        }

        return value.length > MAX_DATA_ITEM_VALUE_LENGTH
          ? t("form.valueTooLong", { max: MAX_DATA_ITEM_VALUE_LENGTH })
          : null;
      },
    },
  });

  const handleError = (error: ApiError): void => {
    if (error.code === "TEST_DATA_KEY_ALREADY_USED") {
      form.setFieldError("key", t("errors.keyAlreadyUsed"));
      return;
    }

    const isEnvironmentScope = form.values.scopeId !== PROJECT_SCOPE_ID;
    const hasFieldErrors = Object.keys(error.fieldErrors).length > 0;
    if (error.code === "INVALID_REQUEST" && isEnvironmentScope && !hasFieldErrors) {
      showErrorToast(t("errors.environmentArchived"));
      return;
    }

    showErrorToast(resolveMessage(error));
  };

  const handleSaved = (item: DataItem, message: string): void => {
    showSuccessToast(message);
    onSaved?.(item);
    onClose();
  };

  const createDataItem = usePostDataItem(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (item) => {
      handleSaved(item, t("toasts.created"));
    },
  });

  const updateDataItem = usePutDataItem(projectKey, {
    isGlobalErrorToastDisabled: true,
    onError: handleError,
    onSuccess: (item) => {
      handleSaved(item, t("toasts.updated"));
    },
  });

  const isSubmitting = createDataItem.isPending || updateDataItem.isPending;
  const isSecret = form.values.kind === "secret";
  const isKeepingSecret = isKeepingSecretValue(editingItem, form.values.kind);

  const scopeOptions: DSSelectOption<string>[] = [
    { value: PROJECT_SCOPE_ID, label: t("grid.allEnvironments") },
    ...environments
      .filter((environment) => !environment.isArchived || environment.id === form.values.scopeId)
      .map((environment) => {
        return { value: environment.id, label: environment.name };
      }),
  ];

  const handleValidSubmit = (values: DataItemFormValues): void => {
    if (editingItem === null) {
      createDataItem.mutate(buildCreateDataItemRequest(values));
      return;
    }

    updateDataItem.mutate({
      itemId: editingItem.id,
      body: buildUpdateDataItemRequest(values, editingItem),
    });
  };

  const handleKeyChange = (value: string): void => {
    form.setFieldValue("key", value);
  };

  const handleSecretChange = (isChecked: boolean): void => {
    form.setFieldValue("kind", isChecked ? "secret" : "variable");
  };

  const handleDescriptionChange = (value: string): void => {
    form.setFieldValue("description", value);
  };

  const handleScopeChange = (scopeId: string | null): void => {
    form.setFieldValue("scopeId", scopeId ?? PROJECT_SCOPE_ID);
  };

  const handleValueChange = (value: string): void => {
    form.setFieldValue("value", value);
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={editingItem === null ? t("form.createTitle") : t("form.editTitle")}
      isCloseDisabled={isSubmitting}
      action={{
        label: editingItem === null ? t("actions.create") : t("actions.save"),
        formId,
        isLoading: isSubmitting,
      }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSInput
            label={t("form.key")}
            description={t("form.keyHint")}
            value={form.values.key}
            onChange={handleKeyChange}
            error={toFormErrorText(form.errors.key)}
            autoComplete="off"
            isDisabled={isFromCell}
            isRequired
            isAutoFocused={!isFromCell}
          />
          <DSSelect
            label={t("form.scope")}
            value={form.values.scopeId}
            options={scopeOptions}
            onChange={handleScopeChange}
            isDisabled={isScopeLocked}
            isRequired
          />
          {isSecret ? (
            <DSPasswordInput
              label={t("form.secretValue")}
              description={isKeepingSecret ? t("form.keepSecretHint") : undefined}
              value={form.values.value}
              onChange={handleValueChange}
              error={form.errors.value}
              autoComplete="new-password"
              isRequired={!isKeepingSecret}
              isAutoFocused={isFromCell}
            />
          ) : (
            <DSTextarea
              label={t("form.value")}
              value={form.values.value}
              onChange={handleValueChange}
              error={form.errors.value}
              minRows={2}
              maxLength={MAX_DATA_ITEM_VALUE_LENGTH}
              isRequired
              isMonospace
            />
          )}
          <DSCheckbox
            label={t("form.secret")}
            description={canEditSecrets ? t("form.secretHint") : t("form.secretLocked")}
            isChecked={isSecret}
            onChange={handleSecretChange}
            isDisabled={!canEditSecrets}
          />
          <DSTextarea
            label={t("form.description")}
            description={t("form.descriptionHint")}
            value={form.values.description}
            onChange={handleDescriptionChange}
            minRows={2}
            maxLength={MAX_DATA_ITEM_DESCRIPTION_LENGTH}
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
