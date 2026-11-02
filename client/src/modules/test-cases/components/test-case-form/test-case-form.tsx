"use client";

import {
  DSButton,
  DSInput,
  DSReferenceTextarea,
  DSSelect,
  DSStepEditor,
  DSText,
  type DSReferenceSuggestion,
  type DSSelectOption,
  type DSStepEditorLabels,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { DataTableEditor } from "@/modules/data-rows/components/data-table-editor/data-table-editor";
import { SharedStepPickerModal } from "@/modules/shared-steps/components/shared-step-picker-modal/shared-step-picker-modal";
import { useId, useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import {
  DATA_REFERENCE_PREFIX,
  FILE_REFERENCE_PREFIX,
  MAX_CRITERION_LINKS,
  MAX_STEPS,
  MAX_TEXT_LENGTH,
  MAX_TITLE_LENGTH,
  TEST_CASE_PRIORITIES,
} from "../../typing/constants/test-case.constant";
import type {
  TestCaseFormErrorKey,
  TestCaseFormErrors,
} from "../../typing/types/test-case-form-errors.type";
import type { TestCaseFormValues } from "../../typing/types/test-case-form-values.type";
import type {
  LinkedCriterion,
  TestCasePriority,
  TestFile,
} from "../../typing/types/test-case.type";
import { createFormStep } from "../../utils/form-step.util";
import { CaseEditorSharedStep } from "../case-editor-shared-step/case-editor-shared-step";
import { CriteriaField } from "../criteria-field/criteria-field";
import { StorySelect } from "../story-select/story-select";
import styles from "./test-case-form.module.scss";

interface Props {
  values: TestCaseFormValues;
  onChange: (values: TestCaseFormValues) => void;
  errors: TestCaseFormErrors | null;
  linkedCriteria: readonly LinkedCriterion[];
  suggestions: readonly DSReferenceSuggestion[];
  files: readonly TestFile[];
  isStoryShown: boolean;
  isStoryLocked: boolean;
  isReadOnly: boolean;
  isSubmitting: boolean;
  isSubmitDisabled: boolean;
  submitLabel: string;
  onSubmit: () => void;
  cancelLabel?: string;
  onCancel?: () => void;
}

export const TestCaseForm: FC<Props> = ({
  values,
  onChange,
  errors,
  linkedCriteria,
  suggestions,
  files,
  isStoryShown,
  isStoryLocked,
  isReadOnly,
  isSubmitting,
  isSubmitDisabled,
  submitLabel,
  onSubmit,
  cancelLabel,
  onCancel,
}) => {
  const { t } = useTranslation("testCases");
  const { t: tSharedSteps } = useTranslation("sharedSteps");
  const { t: tDataRows } = useTranslation("dataRows");
  const project = useCurrentProject();
  const stepsTitleId = useId();
  const dataTitleId = useId();
  const [isPickerOpened, setIsPickerOpened] = useState(false);

  const translateError = (
    errorKey: TestCaseFormErrorKey | undefined,
    max: number,
  ): string | undefined => {
    if (errorKey === undefined) {
      return undefined;
    }

    return errorKey === "required" ? t("form.required") : t(`form.${errorKey}`, { max });
  };

  const priorityOptions: DSSelectOption<TestCasePriority>[] = TEST_CASE_PRIORITIES.map(
    (priority) => {
      return { value: priority, label: t(`priority.${priority}`) };
    },
  );

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
      return [stepId, translateError(errorKey, MAX_TEXT_LENGTH) ?? ""];
    }),
  );

  const changeValue = <Field extends keyof TestCaseFormValues>(
    field: Field,
    value: TestCaseFormValues[Field],
  ): void => {
    onChange({ ...values, [field]: value });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (!isReadOnly && !isSubmitDisabled) {
      onSubmit();
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {isStoryShown && (
        <StorySelect
          label={t("form.story")}
          placeholder={t("form.storyPlaceholder")}
          value={values.storyKey}
          onChange={(storyKey) => {
            onChange({ ...values, storyKey, criterionIds: [] });
          }}
          error={translateError(errors?.storyKey, 0)}
          isRequired
          isDisabled={isStoryLocked || isReadOnly}
        />
      )}
      <div className={styles.row}>
        <div className={styles.title}>
          <DSInput
            label={t("form.title")}
            value={values.title}
            onChange={(title) => {
              changeValue("title", title.slice(0, MAX_TITLE_LENGTH));
            }}
            error={translateError(errors?.title, MAX_TITLE_LENGTH)}
            isRequired
            isDisabled={isReadOnly}
          />
        </div>
        <DSSelect<TestCasePriority>
          label={t("form.priority")}
          value={values.priority}
          options={priorityOptions}
          onChange={(priority) => {
            if (priority !== null) {
              changeValue("priority", priority);
            }
          }}
          isRequired
          isDisabled={isReadOnly}
        />
      </div>
      <div className={styles.row}>
        <DSReferenceTextarea
          label={t("form.businessValue")}
          value={values.businessValue}
          onChange={(businessValue) => {
            changeValue("businessValue", businessValue);
          }}
          suggestions={suggestions}
          suggestionsLabel={t("form.suggestions")}
          noSuggestionsLabel={t("form.noSuggestions")}
          error={translateError(errors?.businessValue, MAX_TEXT_LENGTH)}
          maxLength={MAX_TEXT_LENGTH}
          isDisabled={isReadOnly}
        />
        <DSReferenceTextarea
          label={t("form.preconditions")}
          value={values.preconditions}
          onChange={(preconditions) => {
            changeValue("preconditions", preconditions);
          }}
          suggestions={suggestions}
          suggestionsLabel={t("form.suggestions")}
          noSuggestionsLabel={t("form.noSuggestions")}
          error={translateError(errors?.preconditions, MAX_TEXT_LENGTH)}
          maxLength={MAX_TEXT_LENGTH}
          isDisabled={isReadOnly}
        />
      </div>
      <CriteriaField
        storyKey={values.storyKey}
        linkedCriteria={linkedCriteria}
        value={values.criterionIds}
        onChange={(criterionIds) => {
          changeValue("criterionIds", criterionIds);
        }}
        error={translateError(errors?.criterionIds, MAX_CRITERION_LINKS)}
        isDisabled={isReadOnly}
      />
      <section className={styles.section} aria-labelledby={stepsTitleId}>
        <h2 id={stepsTitleId} className={styles.sectionTitle}>
          {t("form.steps")}
        </h2>
        {!isReadOnly && (
          <DSText size="sm" color="muted">
            {t("form.referenceHint", { data: DATA_REFERENCE_PREFIX, file: FILE_REFERENCE_PREFIX })}
          </DSText>
        )}
        <DSStepEditor
          steps={values.steps}
          onChange={(steps) => {
            changeValue("steps", steps);
          }}
          suggestions={suggestions}
          labels={stepLabels}
          maxSteps={MAX_STEPS}
          maxTextLength={MAX_TEXT_LENGTH}
          errors={stepErrors}
          isDisabled={isReadOnly}
          renderSharedStep={(step) => {
            return <CaseEditorSharedStep sharedStepKey={step.sharedStepKey ?? ""} files={files} />;
          }}
          footerActions={
            <DSButton
              type="default"
              icon="sharedSteps"
              isDisabled={values.steps.length >= MAX_STEPS}
              ariaHasPopup="dialog"
              onClick={() => {
                setIsPickerOpened(true);
              }}
            >
              {tSharedSteps("picker.open")}
            </DSButton>
          }
        />
      </section>
      <section className={styles.section} aria-labelledby={dataTitleId}>
        <h2 id={dataTitleId} className={styles.sectionTitle}>
          {tDataRows("editor.title")}
        </h2>
        <DataTableEditor
          value={values.dataTable}
          onChange={(dataTable) => {
            changeValue("dataTable", dataTable);
          }}
          errors={errors?.dataTable ?? null}
          isDisabled={isReadOnly}
        />
      </section>
      {isPickerOpened && (
        <SharedStepPickerModal
          projectKey={project.key}
          onClose={() => {
            setIsPickerOpened(false);
          }}
          onInsert={(sharedStepKey) => {
            changeValue("steps", [...values.steps, createFormStep("", "", sharedStepKey)]);
            setIsPickerOpened(false);
          }}
        />
      )}
      {!isReadOnly && (
        <div className={styles.footer}>
          {onCancel !== undefined && (
            <DSButton type="default" isDisabled={isSubmitting} onClick={onCancel}>
              {cancelLabel}
            </DSButton>
          )}
          <DSButton
            type="primary"
            nativeType="submit"
            isLoading={isSubmitting}
            isDisabled={isSubmitDisabled}
          >
            {submitLabel}
          </DSButton>
        </div>
      )}
    </form>
  );
};
