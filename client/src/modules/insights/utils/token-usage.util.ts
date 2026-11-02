import type { DSChartDatum } from "@/components/design-system";
import { CATEGORY_KEY, TOKEN_CHART_RUN_COUNT } from "../typing/constants/insights.constant";
import type { TokenRun } from "../typing/types/insights.type";

export const describeTokenRunSource = (run: TokenRun): string => {
  return run.storyJiraKey ?? run.testSuiteName ?? run.runId;
};

export const buildTokenChartData = (
  runs: TokenRun[],
  labelRun: (run: TokenRun) => string,
): DSChartDatum[] => {
  return runs
    .slice(0, TOKEN_CHART_RUN_COUNT)
    .reverse()
    .map((run) => {
      return {
        [CATEGORY_KEY]: labelRun(run),
        input: run.inputTokens,
        cacheWrite: run.cacheCreationInputTokens,
        cacheRead: run.cacheReadInputTokens,
        output: run.outputTokens,
      };
    });
};
