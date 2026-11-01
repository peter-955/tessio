"use client";

import {
  DSPageHeader,
  DSStack,
  DSTabPanel,
  DSTabs,
  type DSTabItem,
} from "@/components/design-system";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { RUNS_TAB_PARAMETER_VALUE, TAB_PARAMETER } from "../../typing/constants/run.constant";
import { RunDetailTab } from "../../typing/enums/run-detail-tab.enum";
import { parseRunDetailTab } from "../../utils/run-detail-tab.util";
import { buildStoryPath } from "../../utils/run-path.util";
import { RunCaseList } from "../run-case-list/run-case-list";
import { RunDetailsCard } from "../run-details-card/run-details-card";
import { RunProgress } from "../run-progress/run-progress";
import { RunReport } from "../run-report/run-report";
import styles from "./run-detail-view.module.scss";

interface Props {
  projectKey: string;
  run: RunDetail;
  initialTab: RunDetailTab;
  actions?: ReactNode;
}

export const RunDetailView: FC<Props> = ({ projectKey, run, initialTab, actions }) => {
  const { t } = useTranslation("runs");
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlTab = parseRunDetailTab(searchParams.get(TAB_PARAMETER));
  const [selectedTab, setSelectedTab] = useState(initialTab);
  const [syncedTab, setSyncedTab] = useState(urlTab);

  if (urlTab !== syncedTab) {
    setSyncedTab(urlTab);
    setSelectedTab(urlTab);
  }

  const activeTab = run.report === null ? RunDetailTab.RESULTS : selectedTab;
  const reportedCount = run.cases.filter((runCase) => {
    return runCase.result !== null;
  }).length;
  const tabItems: DSTabItem<RunDetailTab>[] = [
    { value: RunDetailTab.RESULTS, label: t("tabs.results"), icon: "testCases" },
    {
      value: RunDetailTab.REPORT,
      label: t("tabs.report"),
      icon: "file",
      isDisabled: run.report === null,
    },
  ];

  const handleTabChange = (tab: RunDetailTab): void => {
    setSelectedTab(tab);
    router.replace(`?${new URLSearchParams({ [TAB_PARAMETER]: tab }).toString()}`, {
      scroll: false,
    });
  };

  return (
    <>
      <DSPageHeader
        title={t("detail.title", { jiraKey: run.storyJiraKey })}
        description={
          <span className={styles.story}>
            <Link href={buildStoryPath(projectKey, run.storyJiraKey, RUNS_TAB_PARAMETER_VALUE)}>
              {run.storyJiraKey}
            </Link>
            <span>{run.storyTitle}</span>
          </span>
        }
        actions={actions}
      />
      <DSStack gap={4}>
        {run.status === "running" && (
          <RunProgress reportedCount={reportedCount} totalCount={run.cases.length} />
        )}
        <RunDetailsCard projectKey={projectKey} run={run} />
        <DSTabs
          items={tabItems}
          value={activeTab}
          onChange={handleTabChange}
          ariaLabel={t("tabs.label")}
        >
          <DSTabPanel value={RunDetailTab.RESULTS}>
            <RunCaseList projectKey={projectKey} run={run} />
          </DSTabPanel>
          <DSTabPanel value={RunDetailTab.REPORT}>
            {run.report !== null && (
              <RunReport projectKey={projectKey} runId={run.id} report={run.report} />
            )}
          </DSTabPanel>
        </DSTabs>
      </DSStack>
    </>
  );
};
