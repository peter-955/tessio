"use client";

import {
  DSButton,
  DSPageHeader,
  DSSegmentedControl,
  type DSSegmentedOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { PlanFormModal } from "./components/plan-form-modal/plan-form-modal";
import { PlanList } from "./components/plan-list/plan-list";
import styles from "./plans.module.scss";
import { PLAN_STATUS_FILTERS } from "./typing/constants/plan.constant";
import type { PlanStatusFilter } from "./typing/types/plan-status-filter.type";
import { checkCanCreatePlan } from "./utils/plan-capability.util";

export const PlansPage: FC = () => {
  const { t } = useTranslation("plans");
  const project = useCurrentProject();
  const [status, setStatus] = useState<PlanStatusFilter>("all");
  const [isCreating, setIsCreating] = useState(false);
  const canCreate = checkCanCreatePlan(project);
  const statusOptions = PLAN_STATUS_FILTERS.map((value): DSSegmentedOption<PlanStatusFilter> => {
    return { value, label: t(`list.filters.${value}`) };
  });
  const createButton = canCreate ? (
    <DSButton
      type="primary"
      icon="plus"
      onClick={() => {
        setIsCreating(true);
      }}
    >
      {t("list.newPlan")}
    </DSButton>
  ) : null;

  return (
    <>
      <DSPageHeader
        title={t("page.title")}
        description={t("page.description")}
        actions={createButton}
      />
      <div className={styles.filters}>
        <DSSegmentedControl<PlanStatusFilter>
          value={status}
          options={statusOptions}
          onChange={setStatus}
          ariaLabel={t("list.statusFilter")}
        />
      </div>
      <PlanList
        projectKey={project.key}
        status={status}
        createAction={createButton}
        onShowAll={() => {
          setStatus("all");
        }}
      />
      {isCreating && (
        <PlanFormModal
          projectKey={project.key}
          plan={null}
          onClose={() => {
            setIsCreating(false);
          }}
        />
      )}
    </>
  );
};
