"use client";

import {
  DSErrorState,
  DSSelect,
  DSSkeleton,
  DSSwitch,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetTestCaseVersions } from "@/modules/test-cases/hooks/queries/use-get-test-case-versions";
import type {
  TestCaseDetail,
  TestCaseVersion,
} from "@/modules/test-cases/typing/types/test-case.type";
import { labelVersionSharedSteps } from "@/modules/test-cases/utils/step-text.util";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useId, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { buildVersionComparison } from "../../utils/version-comparison.util";
import { CompareTable } from "../compare-table/compare-table";
import styles from "./compare-versions.module.scss";

interface Props {
  detail: TestCaseDetail;
}

export const CompareVersions: FC<Props> = ({ detail }) => {
  const { t } = useTranslation("caseReview");
  const { t: tSharedSteps } = useTranslation("sharedSteps");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const titleId = useId();
  const [olderId, setOlderId] = useState<string | null>(null);
  const [newerId, setNewerId] = useState<string | null>(null);
  const [isOnlyChanges, setIsOnlyChanges] = useState(false);
  const { data, isPending, isError, isFetching, refetch } = useGetTestCaseVersions(
    project.key,
    detail.code,
  );
  const { data: members = [] } = useGetProjectMembers(project.key);

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
          title={t("compare.loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    const olderVersion = data.find((version) => version.id === olderId) ?? data[1] ?? null;
    const newerVersion = data.find((version) => version.id === newerId) ?? data[0] ?? null;

    if (olderVersion === null || newerVersion === null) {
      return <DSText color="muted">{t("compare.single")}</DSText>;
    }

    const memberNames = new Map(members.map((member) => [member.userId, member.name]));
    const versionOptions = data.map((version): DSSelectOption<string> => {
      return {
        value: version.id,
        label:
          version.id === detail.currentVersion.id
            ? t("compare.currentOption", { number: version.number })
            : t("compare.versionOption", { number: version.number }),
      };
    });
    const describeVersion = (version: TestCaseVersion): string => {
      return t("compare.heading", {
        number: version.number,
        name: memberNames.get(version.createdBy) ?? t("compare.formerMember"),
        date: formatDate(version.createdAt),
      });
    };
    const formatSharedStep = (sharedStepKey: string): string => {
      return tSharedSteps("reference.textLabel", { key: sharedStepKey });
    };
    const comparison = buildVersionComparison(
      labelVersionSharedSteps(olderVersion, formatSharedStep),
      labelVersionSharedSteps(newerVersion, formatSharedStep),
    );

    return (
      <>
        <div className={styles.toolbar}>
          <DSSelect<string>
            label={t("compare.from")}
            value={olderVersion.id}
            options={versionOptions}
            onChange={setOlderId}
          />
          <DSSelect<string>
            label={t("compare.to")}
            value={newerVersion.id}
            options={versionOptions}
            onChange={setNewerId}
          />
          <div className={styles.switch}>
            <DSSwitch
              label={t("compare.onlyChanges")}
              isChecked={isOnlyChanges}
              onChange={setIsOnlyChanges}
            />
          </div>
        </div>
        <DSText size="sm" color="muted">
          {comparison.changeCount === 0
            ? t("compare.identical")
            : t("compare.changeCount", { count: comparison.changeCount })}
        </DSText>
        {(comparison.changeCount > 0 || !isOnlyChanges) && (
          <CompareTable
            comparison={comparison}
            olderHeading={describeVersion(olderVersion)}
            newerHeading={describeVersion(newerVersion)}
            label={t("compare.tableLabel", {
              from: olderVersion.number,
              to: newerVersion.number,
            })}
            isOnlyChanges={isOnlyChanges}
          />
        )}
      </>
    );
  };

  return (
    <section aria-labelledby={titleId} className={styles.compare}>
      <div className={styles.intro}>
        <h2 id={titleId} className={styles.heading}>
          {t("compare.title")}
        </h2>
        <DSText size="sm" color="muted">
          {t("compare.description")}
        </DSText>
      </div>
      {renderBody()}
    </section>
  );
};
