"use client";

import { DSErrorState, DSPageHeader, DSSkeleton, DSStack } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./ai-harness.module.scss";
import { CommandsCard } from "./components/commands-card/commands-card";
import { HooksCard } from "./components/hooks-card/hooks-card";
import { McpServerCard } from "./components/mcp-server-card/mcp-server-card";
import { SkillsCard } from "./components/skills-card/skills-card";
import { VersionsCard } from "./components/versions-card/versions-card";
import { useGetAiHarness } from "./hooks/queries/use-get-ai-harness";

const PAGE_SKELETON_LINE_COUNT = 8;

export const AiHarnessPage: FC = () => {
  const { t } = useTranslation("aiHarness");
  const { data: harness, isPending, isError, refetch, isRefetching } = useGetAiHarness();

  const handleRetry = (): void => {
    void refetch();
  };

  let content = <DSSkeleton lineCount={PAGE_SKELETON_LINE_COUNT} />;
  if (isError) {
    content = (
      <DSErrorState
        title={t("loadFailed")}
        retryLabel={t("retry")}
        onRetry={handleRetry}
        isRetrying={isRefetching}
      />
    );
  } else if (!isPending && harness !== undefined) {
    content = (
      <>
        <VersionsCard harness={harness} />
        <SkillsCard skills={harness.skills} />
        <CommandsCard commands={harness.commands} />
        <HooksCard hooks={harness.hooks} />
        <McpServerCard servers={harness.mcpServers} tools={harness.mcpTools} />
      </>
    );
  }

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} />
      <DSStack gap={5} className={styles.content}>
        {content}
      </DSStack>
    </>
  );
};
