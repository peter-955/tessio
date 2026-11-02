import { LIVE_EVENT_QUERY_KEYS } from "@/shared/typing/constants/live-event-query-keys.constant";
import { LiveEventType } from "@/shared/typing/enums/live-event-type.enum";
import { describe, expect, it } from "vitest";
import { GET_FLAKY_CASES_KEY } from "./queries/use-get-flaky-cases";
import { GET_INSIGHT_TRENDS_KEY } from "./queries/use-get-insight-trends";
import { GET_LABEL_COVERAGE_KEY } from "./queries/use-get-label-coverage";
import { GET_SPRINT_COVERAGE_KEY } from "./queries/use-get-sprint-coverage";
import { GET_TOKEN_USAGE_KEY } from "./queries/use-get-token-usage";
import { GET_TOP_FAILING_CASES_KEY } from "./queries/use-get-top-failing-cases";

describe("insight live events", () => {
  it("refreshes every insight on insights.changed", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.INSIGHTS_CHANGED]).toEqual(
      expect.arrayContaining([
        GET_INSIGHT_TRENDS_KEY,
        GET_LABEL_COVERAGE_KEY,
        GET_TOP_FAILING_CASES_KEY,
        GET_FLAKY_CASES_KEY,
        GET_TOKEN_USAGE_KEY,
        GET_SPRINT_COVERAGE_KEY,
      ]),
    );
  });

  it("refreshes every insight when a run finishes", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.RUN_FINISHED]).toEqual(
      expect.arrayContaining([
        GET_INSIGHT_TRENDS_KEY,
        GET_LABEL_COVERAGE_KEY,
        GET_TOP_FAILING_CASES_KEY,
        GET_FLAKY_CASES_KEY,
        GET_TOKEN_USAGE_KEY,
        GET_SPRINT_COVERAGE_KEY,
      ]),
    );
  });

  it("refreshes the result-based insights when a case result is recorded", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.RUN_CASE_RECORDED]).toEqual(
      expect.arrayContaining([
        GET_INSIGHT_TRENDS_KEY,
        GET_LABEL_COVERAGE_KEY,
        GET_TOP_FAILING_CASES_KEY,
        GET_FLAKY_CASES_KEY,
        GET_SPRINT_COVERAGE_KEY,
      ]),
    );
  });

  it.each([LiveEventType.RUN_STARTED, LiveEventType.FAILURE_CHANGED, LiveEventType.GAP_CHANGED])(
    "refreshes today's trends on %s",
    (eventType) => {
      expect(LIVE_EVENT_QUERY_KEYS[eventType]).toContain(GET_INSIGHT_TRENDS_KEY);
    },
  );

  it("refreshes the tokens when a run log arrives", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.RUN_LOG_RECEIVED]).toContain(GET_TOKEN_USAGE_KEY);
  });

  it.each([LiveEventType.TEST_CASE_CHANGED, LiveEventType.LABEL_CHANGED])(
    "refreshes the coverage by label on %s",
    (eventType) => {
      expect(LIVE_EVENT_QUERY_KEYS[eventType]).toContain(GET_LABEL_COVERAGE_KEY);
    },
  );

  it.each([
    LiveEventType.TEST_CASE_CHANGED,
    LiveEventType.STORY_CHANGED,
    LiveEventType.JIRA_SYNC_FINISHED,
  ])("refreshes the sprint coverage on %s", (eventType) => {
    expect(LIVE_EVENT_QUERY_KEYS[eventType]).toContain(GET_SPRINT_COVERAGE_KEY);
  });
});
