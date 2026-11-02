"use client";

import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSPageHeader,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { ExportReportButton } from "@/modules/reports/components/export-report-button/export-report-button";
import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { PlanDialog } from "../../typing/types/plan-dialog.type";
import type { PlanDetail } from "../../typing/types/plan.type";
import {
  checkCanClosePlan,
  checkCanEditPlan,
  checkCanSignOffPlan,
} from "../../utils/plan-capability.util";
import { buildPlansPath } from "../../utils/plan-path.util";
import { PlanCloseModal } from "../plan-close-modal/plan-close-modal";
import { PlanFormModal } from "../plan-form-modal/plan-form-modal";
import { PlanItemsModal } from "../plan-items-modal/plan-items-modal";
import { PlanSignOffModal } from "../plan-sign-off-modal/plan-sign-off-modal";
import { PlanStatusBadge } from "../plan-status-badge/plan-status-badge";
import styles from "./plan-header.module.scss";

interface Props {
  plan: PlanDetail;
}

export const PlanHeader: FC<Props> = ({ plan }) => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();
  const formatDay = useFormatDay();
  const formatDate = useFormatDate();
  const [dialog, setDialog] = useState<PlanDialog | null>(null);
  const canEdit = checkCanEditPlan(project, plan);
  const canSignOff = checkCanSignOffPlan(project, plan);
  const canClose = checkCanClosePlan(project, plan);
  const unknownUser = t("detail.unknownUser");

  const closeDialog = (): void => {
    setDialog(null);
  };

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildPlansPath(project.key)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={plan.name}
        description={plan.description ?? undefined}
        actions={
          <>
            <ExportReportButton target={{ source: "plan", planId: plan.id }} />
            {canEdit && (
              <DSButton
                type="default"
                icon="edit"
                onClick={() => {
                  setDialog("edit");
                }}
              >
                {t("actions.edit")}
              </DSButton>
            )}
            {canEdit && (
              <DSButton
                type="default"
                icon="suites"
                onClick={() => {
                  setDialog("items");
                }}
              >
                {t("actions.chooseItems")}
              </DSButton>
            )}
            {canClose && (
              <DSButton
                type="default"
                onClick={() => {
                  setDialog("close");
                }}
              >
                {t("actions.close")}
              </DSButton>
            )}
            {canSignOff && (
              <DSButton
                type="primary"
                icon="circleCheck"
                onClick={() => {
                  setDialog("signOff");
                }}
              >
                {t("actions.signOff")}
              </DSButton>
            )}
          </>
        }
      />
      <div className={styles.meta}>
        <PlanStatusBadge status={plan.status} />
        <div className={styles.fact}>
          <DSText size="xs" color="muted" component="span">
            {t("detail.targetDate")}
          </DSText>
          <DSText size="sm" component="span">
            {plan.targetDate === null ? t("detail.noTargetDate") : formatDay(plan.targetDate)}
          </DSText>
        </div>
        <div className={styles.fact}>
          <DSText size="xs" color="muted" component="span">
            {t("detail.environment")}
          </DSText>
          <DSText size="sm" component="span">
            {plan.environmentName ?? t("detail.anyEnvironment")}
          </DSText>
        </div>
        <DSStack gap={1}>
          <DSText size="xs" color="muted" component="span">
            {t("detail.createdBy", {
              name: plan.createdByName ?? unknownUser,
              date: formatDate(plan.createdAt),
            })}
          </DSText>
          {plan.signedOffAt !== null && (
            <DSText size="xs" color="muted" component="span">
              {t("detail.signedOffBy", {
                name: plan.signedOffByName ?? unknownUser,
                date: formatDate(plan.signedOffAt),
              })}
            </DSText>
          )}
          {plan.closedAt !== null && (
            <DSText size="xs" color="muted" component="span">
              {t("detail.closedBy", {
                name: plan.closedByName ?? unknownUser,
                date: formatDate(plan.closedAt),
              })}
            </DSText>
          )}
        </DSStack>
      </div>
      {project.isArchived && (
        <div className={styles.back}>
          <DSAlert color="info">{t("detail.readOnlyArchived")}</DSAlert>
        </div>
      )}
      {dialog === "edit" && (
        <PlanFormModal projectKey={project.key} plan={plan} onClose={closeDialog} />
      )}
      {dialog === "items" && (
        <PlanItemsModal projectKey={project.key} plan={plan} onClose={closeDialog} />
      )}
      {dialog === "signOff" && (
        <PlanSignOffModal projectKey={project.key} plan={plan} onClose={closeDialog} />
      )}
      {dialog === "close" && (
        <PlanCloseModal projectKey={project.key} plan={plan} onClose={closeDialog} />
      )}
    </>
  );
};
