"use client";

import {
  DSBadge,
  DSErrorState,
  DSSelect,
  DSSkeleton,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetStory } from "@/modules/stories/hooks/queries/use-get-story";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useId, useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetTestCaseVersions } from "../../hooks/queries/use-get-test-case-versions";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import { labelVersionSharedSteps } from "../../utils/step-text.util";
import { buildVersionDiff } from "../../utils/version-diff.util";
import { VersionDiff } from "../version-diff/version-diff";
import styles from "./version-history.module.scss";

interface Props {
  detail: TestCaseDetail;
  initialFromVersionNumber: number | null;
}

export const VersionHistory: FC<Props> = ({ detail, initialFromVersionNumber }) => {
  const { t } = useTranslation("testCases");
  const { t: tSharedSteps } = useTranslation("sharedSteps");
  const project = useCurrentProject();
  const formatSharedStep = (sharedStepKey: string): string => {
    return tSharedSteps("reference.textLabel", { key: sharedStepKey });
  };
  const formatDate = useFormatDate();
  const versionsTitleId = useId();
  const compareTitleId = useId();
  const [fromId, setFromId] = useState<string | null>(null);
  const [toId, setToId] = useState<string | null>(null);
  const { data, isPending, isError, isFetching, refetch } = useGetTestCaseVersions(
    project.key,
    detail.code,
  );
  const { data: members = [] } = useGetProjectMembers(project.key);
  const { data: story } = useGetStory(project.key, detail.story.jiraKey);

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
        title={t("history.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  const memberNames = new Map(members.map((member) => [member.userId, member.name]));
  const criteria = [...detail.criteria, ...(story?.criteria ?? [])];
  const versionOptions = data.map((version): DSSelectOption<string> => {
    return { value: version.id, label: t("detail.version", { number: version.number }) };
  });
  const linkedVersion = data.find((version) => version.number === initialFromVersionNumber);
  const fromVersion =
    data.find((version) => version.id === fromId) ?? linkedVersion ?? data[1] ?? data[0] ?? null;
  const toVersion = data.find((version) => version.id === toId) ?? data[0] ?? null;

  return (
    <div className={styles.history}>
      <section aria-labelledby={versionsTitleId}>
        <h2 id={versionsTitleId} className={styles.heading}>
          {t("history.versionsLabel")}
        </h2>
        <ol className={styles.versions}>
          {data.map((version) => {
            return (
              <li key={version.id} className={styles.version}>
                <span className={styles.versionTitle}>
                  {t("detail.version", { number: version.number })}
                  {version.id === detail.currentVersion.id && (
                    <DSBadge color="tessio">{t("history.current")}</DSBadge>
                  )}
                </span>
                <span className={styles.muted}>
                  {t("history.savedBy", {
                    name: memberNames.get(version.createdBy) ?? t("history.formerMember"),
                  })}
                </span>
                <span className={styles.muted}>{formatDate(version.createdAt)}</span>
              </li>
            );
          })}
        </ol>
      </section>
      <section aria-labelledby={compareTitleId} className={styles.compare}>
        <h2 id={compareTitleId} className={styles.heading}>
          {t("history.compare")}
        </h2>
        {data.length < 2 || fromVersion === null || toVersion === null ? (
          <DSText color="muted">{t("history.single")}</DSText>
        ) : (
          <>
            <div className={styles.selects}>
              <DSSelect<string>
                label={t("history.from")}
                value={fromVersion.id}
                options={versionOptions}
                onChange={setFromId}
              />
              <DSSelect<string>
                label={t("history.to")}
                value={toVersion.id}
                options={versionOptions}
                onChange={setToId}
              />
            </div>
            <VersionDiff
              entries={buildVersionDiff(
                labelVersionSharedSteps(fromVersion, formatSharedStep),
                labelVersionSharedSteps(toVersion, formatSharedStep),
                criteria,
              )}
            />
          </>
        )}
      </section>
    </div>
  );
};
