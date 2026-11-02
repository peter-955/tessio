"use client";

import { DSCode, DSCopyButton, DSGroup, DSTable, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { AiHarnessSlashCommand } from "../../typing/types/ai-harness.type";
import { buildSlashCommandUsage } from "../../utils/slash-command.util";

interface Props {
  entries: readonly AiHarnessSlashCommand[];
  label: string;
}

export const SlashCommandTable: FC<Props> = ({ entries, label }) => {
  const { t } = useTranslation("aiHarness");

  return (
    <DSTable label={label}>
      <thead>
        <tr>
          <th scope="col">{t("skills.command")}</th>
          <th scope="col">{t("skills.description")}</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => {
          return (
            <tr key={entry.name}>
              <td>
                <DSGroup gap={1} isWrapping={false}>
                  <DSCode>{buildSlashCommandUsage(entry)}</DSCode>
                  <DSCopyButton
                    value={entry.command}
                    label={t("skills.copy", { command: entry.command })}
                  />
                </DSGroup>
              </td>
              <td>
                <DSText size="sm" component="span">
                  {entry.description}
                </DSText>
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
