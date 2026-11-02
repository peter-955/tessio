"use client";

import { DSCard, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { AiHarnessSlashCommand } from "../../typing/types/ai-harness.type";
import { SlashCommandTable } from "../slash-command-table/slash-command-table";

interface Props {
  skills: readonly AiHarnessSlashCommand[];
}

export const SkillsCard: FC<Props> = ({ skills }) => {
  const { t } = useTranslation("aiHarness");

  return (
    <DSCard title={t("skills.title")}>
      {skills.length === 0 ? (
        <DSEmptyState title={t("skills.empty")} size="sm" titleOrder={3} />
      ) : (
        <SlashCommandTable entries={skills} label={t("skills.label")} />
      )}
    </DSCard>
  );
};
