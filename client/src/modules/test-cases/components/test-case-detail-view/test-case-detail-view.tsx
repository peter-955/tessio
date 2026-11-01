"use client";

import { DSAlert, DSButton, DSTabPanel, DSTabs, type DSTabItem } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePatchTestCase } from "../../hooks/mutations/use-patch-test-case";
import { useReferenceSuggestions } from "../../hooks/use-reference-suggestions";
import { useTestCaseEditor } from "../../hooks/use-test-case-editor";
import { TEST_CASE_DETAIL_TAB_PARAMETER } from "../../typing/constants/test-case.constant";
import { TestCaseDetailTab } from "../../typing/enums/test-case-detail-tab.enum";
import type { TestCaseFormErrors } from "../../typing/types/test-case-form-errors.type";
import type { TestCaseFormValues } from "../../typing/types/test-case-form-values.type";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import {
  checkCanEditTestCases,
  checkIsTestCaseReadOnly,
} from "../../utils/test-case-capability.util";
import { checkHasTestCaseFormErrors, validateTestCaseForm } from "../../utils/test-case-form.util";
import { findTestCaseSaveError } from "../../utils/test-case-save-error.util";
import { parseTestCaseTab } from "../../utils/test-case-tab.util";
import { TestCaseAlerts } from "../test-case-alerts/test-case-alerts";
import { TestCaseFiles } from "../test-case-files/test-case-files";
import { TestCaseForm } from "../test-case-form/test-case-form";
import { TestCaseHeader } from "../test-case-header/test-case-header";
import { VersionHistory } from "../version-history/version-history";
import styles from "./test-case-detail-view.module.scss";

interface Props {
  detail: TestCaseDetail;
  initialTab: TestCaseDetailTab;
  onReload: () => Promise<TestCaseDetail | undefined>;
}

export const TestCaseDetailView: FC<Props> = ({ detail, initialTab, onReload }) => {
  const { t } = useTranslation("testCases");
  const router = useRouter();
  const searchParams = useSearchParams();
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast, showErrorToast } = useShowToast();
  const urlTab = parseTestCaseTab(searchParams.get(TEST_CASE_DETAIL_TAB_PARAMETER) ?? undefined);
  const [activeTab, setActiveTab] = useState(initialTab);
  const [syncedTab, setSyncedTab] = useState(urlTab);
  const [errors, setErrors] = useState<TestCaseFormErrors | null>(null);
  const [isConflicted, setIsConflicted] = useState(false);
  const [isReloading, setIsReloading] = useState(false);
  const editor = useTestCaseEditor(detail);
  const suggestions = useReferenceSuggestions(project.key, detail.files);
  const canEdit = checkCanEditTestCases(project);
  const isReadOnly = checkIsTestCaseReadOnly(project, detail.status);
  const updateTestCase = usePatchTestCase(project.key, detail.code, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (savedDetail) => {
      editor.markSaved(savedDetail);
      showSuccessToast(t("toasts.saved", { number: savedDetail.currentVersion.number }));
    },
    onError: (error: ApiError) => {
      const saveError = findTestCaseSaveError(error);
      if (saveError === "versionConflict") {
        setIsConflicted(true);
        return;
      }

      showErrorToast(
        saveError === "criterionNotLinkable"
          ? t("errors.criterionNotLinkable")
          : resolveMessage(error),
      );
    },
  });

  if (urlTab !== syncedTab) {
    setSyncedTab(urlTab);
    setActiveTab(urlTab);
  }

  const tabItems: DSTabItem<TestCaseDetailTab>[] = [
    { value: TestCaseDetailTab.DETAILS, label: t("detail.tabs.details"), icon: "testCases" },
    {
      value: TestCaseDetailTab.FILES,
      label: t("detail.tabs.files"),
      icon: "file",
      count: detail.files.length,
    },
    { value: TestCaseDetailTab.HISTORY, label: t("detail.tabs.history"), icon: "restore" },
  ];

  const handleTabChange = (tab: TestCaseDetailTab): void => {
    setActiveTab(tab);
    router.replace(`?${TEST_CASE_DETAIL_TAB_PARAMETER}=${tab}`, { scroll: false });
  };

  const handleChange = (values: TestCaseFormValues): void => {
    editor.changeValues(values);
    if (errors !== null) {
      setErrors(validateTestCaseForm(values));
    }
  };

  const handleSubmit = (): void => {
    const nextErrors = validateTestCaseForm(editor.values);
    setErrors(nextErrors);
    if (checkHasTestCaseFormErrors(nextErrors) || !editor.isDirty) {
      return;
    }

    updateTestCase.mutate(editor.updateRequest);
  };

  const handleReload = async (): Promise<void> => {
    setIsReloading(true);
    try {
      const latestDetail = await onReload();
      if (latestDetail !== undefined) {
        editor.resetTo(latestDetail);
        setErrors(null);
        setIsConflicted(false);
      }
    } finally {
      setIsReloading(false);
    }
  };

  return (
    <>
      <TestCaseHeader
        projectKey={project.key}
        detail={detail}
        isDirty={editor.isDirty}
        canEdit={canEdit}
      />
      <TestCaseAlerts detail={detail} canEdit={canEdit} />
      <DSTabs
        items={tabItems}
        value={activeTab}
        onChange={handleTabChange}
        ariaLabel={t("detail.tabs.ariaLabel")}
      >
        <DSTabPanel value={TestCaseDetailTab.DETAILS}>
          <div className={styles.panel}>
            {!canEdit && <DSAlert color="info">{t("form.readOnly")}</DSAlert>}
            {isConflicted && (
              <DSAlert
                color="danger"
                action={
                  <DSButton
                    type="default"
                    size="sm"
                    icon="refresh"
                    isLoading={isReloading}
                    onClick={() => {
                      void handleReload();
                    }}
                  >
                    {t("actions.reload")}
                  </DSButton>
                }
              >
                {t("errors.versionConflict")}
              </DSAlert>
            )}
            <TestCaseForm
              values={editor.values}
              onChange={handleChange}
              errors={errors}
              linkedCriteria={detail.criteria}
              suggestions={suggestions}
              isStoryShown={false}
              isStoryLocked
              isReadOnly={isReadOnly}
              isSubmitting={updateTestCase.isPending}
              isSubmitDisabled={!editor.isDirty || updateTestCase.isPending}
              submitLabel={updateTestCase.isPending ? t("actions.saving") : t("actions.save")}
              onSubmit={handleSubmit}
            />
          </div>
        </DSTabPanel>
        <DSTabPanel value={TestCaseDetailTab.FILES}>
          <div className={styles.panel}>
            <TestCaseFiles
              detail={detail}
              canAttach={!isReadOnly}
              hasUnsavedChanges={editor.isDirty}
            />
          </div>
        </DSTabPanel>
        <DSTabPanel value={TestCaseDetailTab.HISTORY}>
          <div className={styles.panel}>
            <VersionHistory detail={detail} />
          </div>
        </DSTabPanel>
      </DSTabs>
    </>
  );
};
