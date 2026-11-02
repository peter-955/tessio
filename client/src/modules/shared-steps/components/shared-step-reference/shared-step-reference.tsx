"use client";

import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { DSBadge, DSButton, DSCode, DSSkeleton, DSText } from "@/components/design-system";
import Link from "next/link";
import { useId, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useFindSharedStep } from "../../hooks/use-find-shared-step";
import { buildSharedStepPath } from "../../utils/shared-step-path.util";
import { SharedStepActions } from "../shared-step-actions/shared-step-actions";
import styles from "./shared-step-reference.module.scss";

interface Props {
  projectKey: string;
  sharedStepKey: string;
  references?: CaseReferences;
}

export const SharedStepReference: FC<Props> = ({ projectKey, sharedStepKey, references }) => {
  const { t } = useTranslation("sharedSteps");
  const stepsId = useId();
  const [isExpanded, setIsExpanded] = useState(false);
  const { sharedStep, isPending, isError } = useFindSharedStep(projectKey, sharedStepKey);

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("reference.loading")}>
        <DSSkeleton height={24} />
      </div>
    );
  }

  if (sharedStep === null) {
    return (
      <div className={styles.reference}>
        <div className={styles.header}>
          <DSBadge color="violet">{t("reference.badge")}</DSBadge>
          <DSCode>{sharedStepKey}</DSCode>
        </div>
        <DSText size="sm" color={isError ? "danger" : "warning"}>
          {isError ? t("reference.loadError") : t("reference.missing")}
        </DSText>
      </div>
    );
  }

  const actions = sharedStep.currentVersion.steps;

  return (
    <div className={styles.reference}>
      <div className={styles.header}>
        <div className={styles.identity}>
          <DSBadge color="violet">{t("reference.badge")}</DSBadge>
          <Link href={buildSharedStepPath(projectKey, sharedStep.key)} className={styles.title}>
            {sharedStep.title}
          </Link>
          <DSCode>{sharedStep.key}</DSCode>
          {sharedStep.isArchived && <DSBadge color="gray">{t("reference.archived")}</DSBadge>}
          <DSText size="sm" color="muted" component="span">
            {t("reference.stepCount", { count: actions.length })}
          </DSText>
        </div>
        <DSButton
          type="ghost"
          size="sm"
          icon={isExpanded ? "eyeOff" : "eye"}
          ariaExpanded={isExpanded}
          ariaControls={stepsId}
          onClick={() => {
            setIsExpanded(!isExpanded);
          }}
        >
          {isExpanded ? t("reference.hideSteps") : t("reference.showSteps")}
        </DSButton>
      </div>
      <div id={stepsId} hidden={!isExpanded} className={styles.steps}>
        {isExpanded && (
          <SharedStepActions
            actions={actions}
            references={references}
            ariaLabel={t("reference.stepsOf", { title: sharedStep.title })}
          />
        )}
      </div>
    </div>
  );
};
