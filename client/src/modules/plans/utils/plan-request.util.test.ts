import { describe, expect, it } from "vitest";
import {
  ENVIRONMENT_ID,
  PLAN_ITEMS,
  STORY_ID,
  SUITE_ID,
  buildPlanDetail,
} from "../test/utils/plan-fixture.util";
import {
  buildCreatePlanRequest,
  buildPlanFormValues,
  buildPlanItemsFormValues,
  buildSetPlanItemsRequest,
  buildUpdatePlanRequest,
  checkHasSamePlanItems,
  countPlanItems,
} from "./plan-request.util";

describe("plan request utils", () => {
  it("trims the create request and leaves out empty optional fields", () => {
    expect(
      buildCreatePlanRequest({
        name: "  Release 4.2 ",
        description: "   ",
        targetDate: null,
        environmentId: null,
      }),
    ).toEqual({ name: "Release 4.2" });
    expect(
      buildCreatePlanRequest({
        name: "Release 4.2",
        description: " Ship it ",
        targetDate: "2026-11-20",
        environmentId: ENVIRONMENT_ID,
      }),
    ).toEqual({
      name: "Release 4.2",
      description: "Ship it",
      targetDate: "2026-11-20",
      environmentId: ENVIRONMENT_ID,
    });
  });

  it("sends only the changed fields on edit, with null to clear", () => {
    const plan = buildPlanDetail();
    const values = buildPlanFormValues(plan);

    expect(buildUpdatePlanRequest(values, plan)).toEqual({});
    expect(
      buildUpdatePlanRequest(
        { ...values, name: "Release 4.3", description: "", environmentId: null },
        plan,
      ),
    ).toEqual({ name: "Release 4.3", description: null, environmentId: null });
    expect(buildUpdatePlanRequest({ ...values, targetDate: null }, plan)).toEqual({
      targetDate: null,
    });
  });

  it("starts an empty form for a new plan", () => {
    expect(buildPlanFormValues(null)).toEqual({
      name: "",
      description: "",
      targetDate: null,
      environmentId: null,
    });
  });

  it("turns the items into suite and story picks and back, suites first", () => {
    const values = buildPlanItemsFormValues(PLAN_ITEMS);

    expect(values).toEqual({ suiteIds: [SUITE_ID], storyIds: [STORY_ID] });
    expect(countPlanItems(values)).toBe(2);
    expect(buildSetPlanItemsRequest(values)).toEqual({
      items: [{ suiteId: SUITE_ID }, { storyId: STORY_ID }],
    });
  });

  it("tells whether the picks change the plan's items", () => {
    expect(checkHasSamePlanItems({ suiteIds: [SUITE_ID], storyIds: [STORY_ID] }, PLAN_ITEMS)).toBe(
      true,
    );
    expect(checkHasSamePlanItems({ suiteIds: [], storyIds: [STORY_ID] }, PLAN_ITEMS)).toBe(false);
  });
});
