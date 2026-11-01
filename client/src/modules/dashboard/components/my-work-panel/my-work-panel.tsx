"use client";

import { DSCard, DSErrorState, DSSkeleton, DSText, DSTitle } from "@/components/design-system";
import { Fragment, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetMyWork } from "../../hooks/queries/use-get-my-work";
import { NOT_FOUND_STATUS } from "../../typing/constants/dashboard.constant";
import type { MyWork, MyWorkSection } from "../../typing/types/my-work.type";
import { DraftCasesList } from "../draft-cases-list/draft-cases-list";
import { FailuresToFixList } from "../failures-to-fix-list/failures-to-fix-list";
import { GapsToAnswerList } from "../gaps-to-answer-list/gaps-to-answer-list";
import { UnassignedFailures } from "../unassigned-failures/unassigned-failures";
import { UncoveredCriteriaList } from "../uncovered-criteria-list/uncovered-criteria-list";
import styles from "./my-work-panel.module.scss";

interface Props {
  projectKey: string;
  sprintId: string | null;
}

export const MyWorkPanel: FC<Props> = ({ projectKey, sprintId }) => {
  const { t } = useTranslation("dashboard");
  const { data, error, isPending, isError, isFetching, refetch } = useGetMyWork(
    projectKey,
    sprintId,
  );

  const renderSection = (section: MyWorkSection, myWork: MyWork): ReactNode => {
    switch (section) {
      case "cases_to_write":
        return (
          <>
            <UncoveredCriteriaList projectKey={projectKey} list={myWork.uncoveredCriteria} />
            <DraftCasesList projectKey={projectKey} list={myWork.draftCases} />
          </>
        );
      case "failures_to_fix":
        return <FailuresToFixList projectKey={projectKey} list={myWork.failuresToFix} />;
      case "gaps_to_answer":
        return <GapsToAnswerList projectKey={projectKey} list={myWork.gapsToAnswer} />;
    }
  };

  const renderContent = (myWork: MyWork): ReactNode => {
    return (
      <div className={styles.content}>
        <UnassignedFailures projectKey={projectKey} count={myWork.unassignedFailureCount} />
        {myWork.sections.length === 0 ? (
          <DSText color="muted">{t("myWork.nothingForRole")}</DSText>
        ) : (
          <div className={styles.sections}>
            {myWork.sections.map((section) => {
              return <Fragment key={section}>{renderSection(section, myWork)}</Fragment>;
            })}
          </div>
        )}
      </div>
    );
  };

  const renderBody = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={6} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("myWork.loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    return renderContent(data);
  };

  if (error?.status === NOT_FOUND_STATUS) {
    return null;
  }

  return (
    <DSCard>
      <div className={styles.header}>
        <DSTitle order={2} type="section">
          {t("myWork.title")}
        </DSTitle>
        {data !== undefined && (
          <DSText size="sm" color="muted" component="span">
            {t("myWork.role", { role: t(`myWork.roles.${data.role}`) })}
          </DSText>
        )}
      </div>
      {renderBody()}
    </DSCard>
  );
};
