import { describe, expect, it } from "vitest";
import {
  PLAN_ITEMS,
  PLAN_STORIES,
  PLAN_SUITES,
  STORY_ID,
  SUITE_ID,
} from "../test/utils/plan-fixture.util";
import { buildEnvironmentOptions } from "./plan-environment-options.util";
import { buildStoryOptions, buildSuiteOptions } from "./plan-item-options.util";

const formatArchived = (name: string): string => {
  return `${name} (archived)`;
};

describe("plan item options", () => {
  it("lists the project's suites and stories", () => {
    expect(buildSuiteOptions(PLAN_SUITES, PLAN_ITEMS, formatArchived)).toEqual([
      { value: SUITE_ID, label: "Checkout regression" },
      { value: PLAN_SUITES[1]?.id, label: "Search regression" },
    ]);
    expect(buildStoryOptions(PLAN_STORIES, PLAN_ITEMS)[0]).toEqual({
      value: STORY_ID,
      label: "SHOP-12 · Checkout",
    });
  });

  it("keeps an archived suite and a story that are already in the plan", () => {
    const archivedItem = { ...PLAN_ITEMS[0]!, archivedAt: "2026-10-30T09:00:00Z" };

    expect(buildSuiteOptions([], [archivedItem], formatArchived)).toEqual([
      { value: SUITE_ID, label: "Checkout regression (archived)" },
    ]);
    expect(buildStoryOptions([], PLAN_ITEMS)).toEqual([
      { value: STORY_ID, label: "SHOP-12 · Checkout" },
    ]);
  });

  it("keeps the plan's environment when it is no longer active", () => {
    expect(
      buildEnvironmentOptions([{ id: "env-1", name: "QA" }], {
        environmentId: "env-2",
        environmentName: "Old staging",
      }),
    ).toEqual([
      { value: "env-1", label: "QA" },
      { value: "env-2", label: "Old staging" },
    ]);
    expect(buildEnvironmentOptions([{ id: "env-1", name: "QA" }], null)).toEqual([
      { value: "env-1", label: "QA" },
    ]);
  });
});
