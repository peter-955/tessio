"use client";

import { DSAlert, DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostTestCaseReview } from "../../hooks/mutations/use-post-test-case-review";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import styles from "./test-case-alerts.module.scss";

interface Props {
  detail: TestCaseDetail;
  canEdit: boolean;
}

const LIST_SEPARATOR = ", ";

export const TestCaseAlerts: FC<Props> = ({ detail, canEdit }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const { showSuccessToast } = useShowToast();
  const markReviewed = usePostTestCaseReview(project.key, detail.code, {
    onSuccess: () => {
      showSuccessToast(t("toasts.reviewed"));
    },
  });
  const criterionCodes = new Map(
    detail.criteria.map((criterion) => [criterion.id, criterion.code]),
  );
  const changedCodes = detail.needsReviewCriterionIds
    .map((criterionId) => criterionCodes.get(criterionId) ?? null)
    .filter((code): code is string => code !== null);
  const unknownReferences = detail.unknownReferences.map((reference) => `{{${reference}}}`);

  return (
    <div className={styles.alerts}>
      {detail.status === "deprecated" && <DSAlert color="info">{t("form.deprecated")}</DSAlert>}
      {detail.needsReview && (
        <DSAlert
          color="warning"
          action={
            canEdit && (
              <DSButton
                type="default"
                size="sm"
                isLoading={markReviewed.isPending}
                onClick={() => {
                  markReviewed.mutate();
                }}
              >
                {t("actions.markReviewed")}
              </DSButton>
            )
          }
        >
          {t("detail.needsReview", { codes: changedCodes.join(LIST_SEPARATOR) })}
        </DSAlert>
      )}
      {unknownReferences.length > 0 && (
        <DSAlert color="warning">
          {t("detail.unknownReferences", { references: unknownReferences.join(LIST_SEPARATOR) })}
        </DSAlert>
      )}
    </div>
  );
};
