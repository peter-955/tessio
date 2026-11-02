import { LIVE_EVENT_QUERY_KEYS } from "@/shared/typing/constants/live-event-query-keys.constant";
import { LiveEventType } from "@/shared/typing/enums/live-event-type.enum";
import { describe, expect, it } from "vitest";
import { GET_PLAN_KEY } from "./queries/use-get-plan";
import { GET_PLANS_KEY } from "./queries/use-get-plans";

describe("plan live events", () => {
  it("refreshes the plans list and the plan on plan.changed", () => {
    expect(LIVE_EVENT_QUERY_KEYS[LiveEventType.PLAN_CHANGED]).toEqual([
      GET_PLANS_KEY,
      GET_PLAN_KEY,
    ]);
  });

  it.each([
    LiveEventType.RUN_CASE_RECORDED,
    LiveEventType.RUN_FINISHED,
    LiveEventType.FAILURE_CHANGED,
    LiveEventType.GAP_CHANGED,
    LiveEventType.SUITE_CHANGED,
    LiveEventType.TEST_CASE_CHANGED,
    LiveEventType.STORY_CHANGED,
  ])("refreshes the plan's progress on %s", (eventType) => {
    expect(LIVE_EVENT_QUERY_KEYS[eventType]).toContain(GET_PLAN_KEY);
  });

  it.each([
    LiveEventType.RUN_CASE_RECORDED,
    LiveEventType.RUN_FINISHED,
    LiveEventType.SUITE_CHANGED,
    LiveEventType.TEST_CASE_CHANGED,
    LiveEventType.STORY_CHANGED,
  ])("refreshes the plans list counts on %s", (eventType) => {
    expect(LIVE_EVENT_QUERY_KEYS[eventType]).toContain(GET_PLANS_KEY);
  });
});
