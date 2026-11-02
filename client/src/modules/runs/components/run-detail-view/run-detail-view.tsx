"use client";

import {
  DSGroup,
  DSPageHeader,
  DSStack,
  DSTabPanel,
  DSTabs,
  type DSTabItem,
} from "@/components/design-system";
import { ExportReportButton } from "@/modules/reports/components/export-report-button/export-report-button";
import { RunLogView } from "@/modules/run-log/components/run-log/run-log";
import { RunSkippedCases } from "@/modules/suites/components/run-skipped-cases/run-skipped-cases";
import { buildSuitePath } from "@/modules/suites/utils/suite-path.util";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { RUNS_TAB_PARAMETER_VALUE, TAB_PARAMETER } from "../../typing/constants/run.constant";
import { RunDetailTab } from "../../typing/enums/run-detail-tab.enum";
import { parseRunDetailTab } from "../../utils/run-detail-tab.util";
import { buildStoryPath } from "../../utils/run-path.util";
import { checkIsUntargetedRun } from "../../utils/run-target.util";
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
  const { t: tSuites } = useTranslation("suites");
  const { t: tJunitImport } = useTranslation("junitImport");
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlTab = parseRunDetailTab(searchParams.get(TAB_PARAMETER));
  const [selectedTab, setSelectedTab] = useState(initialTab);
  const [syncedTab, setSyncedTab] = useState(urlTab);

  if (urlTab !== syncedTab) {
    setSyncedTab(urlTab);
    setSelectedTab(urlTab);
  }

  const isClaudeRun = run.executor === "claude";
  const isTabUnavailable =
    (selectedTab === RunDetailTab.REPORT && run.report === null) ||
    (selectedTab === RunDetailTab.LOG && !isClaudeRun);
  const activeTab = isTabUnavailable ? RunDetailTab.RESULTS : selectedTab;
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
    ...(isClaudeRun
      ? [{ value: RunDetailTab.LOG, label: t("tabs.log"), icon: "runs" as const }]
      : []),
  ];

  const suiteId = run.testSuiteId ?? null;
  const isUntargetedRun = checkIsUntargetedRun(run);

  const buildHeader = (): { title: string; description: ReactNode } => {
    if (isUntargetedRun) {
      return {
        title: tJunitImport("ciRun.detailTitle"),
        description: tJunitImport("ciRun.detailDescription"),
      };
    }

    if (suiteId === null || run.storyJiraKey !== null) {
      return {
        title: t("detail.title", { jiraKey: run.storyJiraKey }),
        description: (
          <span className={styles.story}>
            <Link
              href={buildStoryPath(projectKey, run.storyJiraKey ?? "", RUNS_TAB_PARAMETER_VALUE)}
            >
              {run.storyJiraKey}
            </Link>
            <span>{run.storyTitle}</span>
          </span>
        ),
      };
    }

    return {
      title: tSuites("runs.detailTitle", { name: run.testSuiteName ?? suiteId }),
      description: (
        <span className={styles.story}>
          <Link href={buildSuitePath(projectKey, suiteId)}>{tSuites("runs.openSuite")}</Link>
        </span>
      ),
    };
  };

  const header = buildHeader();

  const handleTabChange = (tab: RunDetailTab): void => {
    setSelectedTab(tab);
    router.replace(`?${new URLSearchParams({ [TAB_PARAMETER]: tab }).toString()}`, {
      scroll: false,
    });
  };

  return (
    <>
      <DSPageHeader
        title={header.title}
        description={header.description}
        actions={
          <DSGroup gap={2} isWrapping>
            {actions}
            <ExportReportButton target={{ source: "run", runId: run.id }} />
          </DSGroup>
        }
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
            <DSStack gap={4}>
              <RunCaseList projectKey={projectKey} run={run} />
              <RunSkippedCases projectKey={projectKey} skippedCases={run.skippedCases ?? []} />
            </DSStack>
          </DSTabPanel>
          <DSTabPanel value={RunDetailTab.REPORT}>
            {run.report !== null && (
              <RunReport
                projectKey={projectKey}
                runId={run.id}
                report={run.report}
                isSuiteRun={suiteId !== null || isUntargetedRun}
              />
            )}
          </DSTabPanel>
          {isClaudeRun && (
            <DSTabPanel value={RunDetailTab.LOG}>
              {activeTab === RunDetailTab.LOG && <RunLogView projectKey={projectKey} run={run} />}
            </DSTabPanel>
          )}
        </DSTabs>
      </DSStack>
    </>
  );
};
