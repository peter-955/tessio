import type {
  FailingCase,
  FlakyCase,
  InsightTrends,
  LabelCoverageReport,
  SprintCoverage,
  TokenRun,
  TokenUsage,
  TrendPoint,
} from "../../typing/types/insights.type";

export const SPRINT_ID = "1b2c3d4e-5f60-4718-8293-a4b5c6d7e8f9";

export const buildTrendPoint = (overrides: Partial<TrendPoint> = {}): TrendPoint => {
  return {
    day: "2026-11-01",
    sprint: null,
    firstDay: "2026-11-01",
    lastDay: "2026-11-01",
    runCount: 2,
    runsByExecutor: [
      { executor: "claude", count: 1 },
      { executor: "manual", count: 1 },
    ],
    passedCount: 6,
    failedCount: 1,
    blockedCount: 1,
    skippedCount: 0,
    passRate: 0.75,
    failuresOpened: 1,
    failuresFixed: 2,
    meanTimeToFixSeconds: 7200,
    gapsOpened: 1,
    gapsAnswered: 1,
    meanGapAnswerSeconds: 86400,
    openGapCount: 3,
    medianOpenGapAgeSeconds: 172800,
    ...overrides,
  };
};

export const buildTrends = (overrides: Partial<InsightTrends> = {}): InsightTrends => {
  return {
    groupBy: "day",
    firstDay: "2026-10-03",
    lastDay: "2026-11-01",
    executors: ["claude", "manual"],
    points: [
      buildTrendPoint({ day: "2026-10-31", firstDay: "2026-10-31", lastDay: "2026-10-31" }),
      buildTrendPoint(),
    ],
    total: buildTrendPoint({
      day: null,
      firstDay: "2026-10-03",
      lastDay: "2026-11-01",
      runCount: 4,
      passRate: 0.8125,
      failuresOpened: 2,
      failuresFixed: 4,
    }),
    ...overrides,
  };
};

export const buildEmptyTrends = (): InsightTrends => {
  const empty = buildTrendPoint({
    runCount: 0,
    runsByExecutor: [],
    passedCount: 0,
    failedCount: 0,
    blockedCount: 0,
    passRate: null,
    failuresOpened: 0,
    failuresFixed: 0,
    meanTimeToFixSeconds: null,
    gapsOpened: 0,
    gapsAnswered: 0,
    meanGapAnswerSeconds: null,
    openGapCount: 0,
    medianOpenGapAgeSeconds: null,
  });

  return buildTrends({ executors: [], points: [empty], total: empty });
};

export const buildLabelCoverage = (): LabelCoverageReport => {
  return {
    labels: [
      {
        labelId: "2c3d4e5f-6071-4829-93a4-b5c6d7e8f9a0",
        name: "checkout",
        color: "blue",
        counts: {
          caseCount: 4,
          readyCount: 3,
          passedCount: 2,
          readyShare: 0.75,
          passedShare: 0.5,
        },
      },
    ],
    unlabelled: { caseCount: 2, readyCount: 1, passedCount: 0, readyShare: 0.5, passedShare: 0 },
    total: { caseCount: 6, readyCount: 4, passedCount: 2, readyShare: 0.6667, passedShare: 0.3333 },
  };
};

export const buildFailingCase = (overrides: Partial<FailingCase> = {}): FailingCase => {
  return {
    testCaseId: "3d4e5f60-7182-4930-a4b5-c6d7e8f9a0b1",
    code: "TC-7",
    title: "Pay with a saved card",
    status: "ready",
    storyJiraKey: "SHOP-1",
    resultCount: 5,
    failedCount: 2,
    blockedCount: 1,
    failRate: 0.6,
    lastFailedAt: "2026-11-01T10:00:00Z",
    isFlaky: true,
    isQuarantined: false,
    ...overrides,
  };
};

export const buildFlakyCase = (overrides: Partial<FlakyCase> = {}): FlakyCase => {
  return {
    testCaseId: "4e5f6071-8293-4a41-b5c6-d7e8f9a0b1c2",
    code: "TC-9",
    title: "Apply a coupon",
    status: "ready",
    storyJiraKey: "SHOP-2",
    flakyScore: 4,
    isFlaky: true,
    flakySince: "2026-10-20T08:00:00Z",
    isDisagreeing: false,
    disagreedAt: null,
    isQuarantined: true,
    quarantinedAt: "2026-10-22T08:00:00Z",
    ...overrides,
  };
};

export const buildTokenRun = (overrides: Partial<TokenRun> = {}): TokenRun => {
  return {
    runId: "5f607182-93a4-4b52-c6d7-e8f9a0b1c2d3",
    startedAt: "2026-11-01T09:00:00Z",
    executor: "claude",
    storyJiraKey: "SHOP-1",
    testSuiteName: null,
    caseCount: 4,
    inputTokens: 1000,
    cacheCreationInputTokens: 200,
    cacheReadInputTokens: 3000,
    outputTokens: 800,
    totalTokens: 5000,
    tokensPerCase: 1250,
    isCut: false,
    ...overrides,
  };
};

export const buildTokenUsage = (overrides: Partial<TokenUsage> = {}): TokenUsage => {
  return {
    firstDay: "2026-10-03",
    lastDay: "2026-11-01",
    runs: [
      buildTokenRun(),
      buildTokenRun({
        runId: "60718293-a4b5-4c63-d7e8-f9a0b1c2d3e4",
        startedAt: "2026-10-30T09:00:00Z",
        storyJiraKey: null,
        testSuiteName: "Checkout regression",
        totalTokens: 3000,
        tokensPerCase: 1000,
        caseCount: 3,
        isCut: true,
      }),
    ],
    totalTokens: 8000,
    meanTokensPerRun: 4000,
    meanTokensPerCase: 1142.9,
    ...overrides,
  };
};

export const buildSprintCoverage = (overrides: Partial<SprintCoverage> = {}): SprintCoverage => {
  return {
    sprint: {
      id: SPRINT_ID,
      name: "Sprint 12",
      state: "active",
      startAt: "2026-10-15T00:00:00Z",
      endAt: "2026-10-29T00:00:00Z",
    },
    storyCount: 3,
    coverage: {
      criterionCount: 10,
      coveredCount: 8,
      passedCount: 5,
      failedCount: 1,
      blockedCount: 1,
      notRunCount: 1,
      uncoveredCount: 2,
    },
    ...overrides,
  };
};
