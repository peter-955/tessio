import { RERUN_COMMAND_PREFIX } from "../typing/constants/manual-run.constant";

export const buildRerunCommand = (runId: string): string => {
  return `${RERUN_COMMAND_PREFIX} ${runId}`;
};
