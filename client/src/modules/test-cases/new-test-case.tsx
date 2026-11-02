"use client";

import { DSAlert, DSButtonLink, DSEmptyState, DSPageHeader } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { TestCaseForm } from "./components/test-case-form/test-case-form";
import { usePostTestCase } from "./hooks/mutations/use-post-test-case";
import { useReferenceSuggestions } from "./hooks/use-reference-suggestions";
import styles from "./new-test-case.module.scss";
import type { TestCaseFormErrors } from "./typing/types/test-case-form-errors.type";
import type { TestCaseFormValues } from "./typing/types/test-case-form-values.type";
import type { TestFile } from "./typing/types/test-case.type";
import { checkCanEditTestCases } from "./utils/test-case-capability.util";
import {
  buildCreateTestCaseRequest,
  checkHasTestCaseFormErrors,
  createEmptyTestCaseFormValues,
  validateTestCaseForm,
} from "./utils/test-case-form.util";
import { buildTestCasePath, buildTestCasesPath } from "./utils/test-case-path.util";
import { findTestCaseSaveError } from "./utils/test-case-save-error.util";

const NO_FILES: TestFile[] = [];

interface Props {
  initialStoryKey: string | null;
}

export const NewTestCasePage: FC<Props> = ({ initialStoryKey }) => {
  const { t } = useTranslation("testCases");
  const router = useRouter();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const canEdit = checkCanEditTestCases(project);
  const [values, setValues] = useState<TestCaseFormValues>(() => {
    return createEmptyTestCaseFormValues(initialStoryKey);
  });
  const [errors, setErrors] = useState<TestCaseFormErrors | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const suggestions = useReferenceSuggestions(project.key, NO_FILES);
  const dataSuggestions = suggestions.filter((suggestion) => suggestion.kind === "data");
  const createTestCase = usePostTestCase(project.key, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (detail) => {
      showSuccessToast(t("toasts.created", { code: detail.code }));
      router.replace(buildTestCasePath(project.key, detail.code));
    },
    onError: (error: ApiError) => {
      const saveError = findTestCaseSaveError(error);
      setSubmitError(
        saveError === "criterionNotLinkable"
          ? t("errors.criterionNotLinkable")
          : resolveMessage(error),
      );
    },
  });

  if (!canEdit) {
    return (
      <DSEmptyState
        title={t("detail.cannotCreate")}
        description={t("detail.cannotCreateDescription")}
        icon="lock"
        action={
          <DSButtonLink href={buildTestCasesPath(project.key)} type="default">
            {t("actions.back")}
          </DSButtonLink>
        }
      />
    );
  }

  const handleChange = (nextValues: TestCaseFormValues): void => {
    setValues(nextValues);
    if (errors !== null) {
      setErrors(validateTestCaseForm(nextValues));
    }
  };

  const handleSubmit = (): void => {
    const nextErrors = validateTestCaseForm(values);
    setErrors(nextErrors);
    setSubmitError(null);
    if (checkHasTestCaseFormErrors(nextErrors) || values.storyKey === null) {
      return;
    }

    createTestCase.mutate(buildCreateTestCaseRequest(values, values.storyKey));
  };

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildTestCasesPath(project.key)} type="ghost">
          {t("actions.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader title={t("form.newTitle")} description={t("form.newDescription")} />
      {submitError !== null && (
        <div className={styles.alert}>
          <DSAlert color="danger">{submitError}</DSAlert>
        </div>
      )}
      <TestCaseForm
        values={values}
        onChange={handleChange}
        errors={errors}
        linkedCriteria={[]}
        suggestions={dataSuggestions}
        files={NO_FILES}
        isStoryShown
        isStoryLocked={initialStoryKey !== null}
        isReadOnly={false}
        isSubmitting={createTestCase.isPending}
        isSubmitDisabled={createTestCase.isPending}
        submitLabel={t("actions.create")}
        onSubmit={handleSubmit}
      />
    </>
  );
};
