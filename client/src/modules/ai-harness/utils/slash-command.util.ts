import type { AiHarnessSlashCommand } from "../typing/types/ai-harness.type";

export const buildSlashCommandUsage = ({
  command,
  argumentHint,
}: AiHarnessSlashCommand): string => {
  return argumentHint === null ? command : `${command} ${argumentHint}`;
};
