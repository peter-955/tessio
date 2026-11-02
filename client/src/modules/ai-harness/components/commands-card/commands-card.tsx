"use client";

import { DSCard, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { AiHarnessSlashCommand } from "../../typing/types/ai-harness.type";
import { SlashCommandTable } from "../slash-command-table/slash-command-table";

interface Props {
  commands: readonly AiHarnessSlashCommand[];
}

export const CommandsCard: FC<Props> = ({ commands }) => {
  const { t } = useTranslation("aiHarness");

  return (
    <DSCard title={t("commands.title")}>
      {commands.length === 0 ? (
        <DSEmptyState
          title={t("commands.empty")}
          description={t("commands.emptyHint")}
          size="sm"
          titleOrder={3}
        />
      ) : (
        <SlashCommandTable entries={commands} label={t("commands.label")} />
      )}
    </DSCard>
  );
};
