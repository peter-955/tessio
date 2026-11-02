import { LIVE_EVENT_QUERY_KEYS } from "@/shared/typing/constants/live-event-query-keys.constant";
import { LiveEventType } from "@/shared/typing/enums/live-event-type.enum";
import { describe, expect, it } from "vitest";
import { GET_SUITE_KEY } from "./queries/use-get-suite";
import { GET_SUITES_KEY } from "./queries/use-get-suites";

describe("suite live events", () => {
  it.each([
    LiveEventType.SUITE_CHANGED,
    LiveEventType.TEST_CASE_CHANGED,
    LiveEventType.RUN_STARTED,
    LiveEventType.RUN_FINISHED,
  ])("refreshes the suites list and the suite on %s", (eventType) => {
    expect(LIVE_EVENT_QUERY_KEYS[eventType]).toEqual(
      expect.arrayContaining([GET_SUITES_KEY, GET_SUITE_KEY]),
    );
  });
});
