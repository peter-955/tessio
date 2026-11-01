import { describe, expect, it } from "vitest";
import { buildCriterion } from "../test/utils/story-fixture.util";
import { sortCriteria } from "./criteria.util";

describe("sortCriteria", () => {
  it("lists active criteria by position, then removed ones", () => {
    const removed = buildCriterion({ id: "r", position: 1, isRemoved: true });
    const second = buildCriterion({ id: "b", position: 3 });
    const first = buildCriterion({ id: "a", position: 2 });

    expect(sortCriteria([removed, second, first]).map(({ id }) => id)).toEqual(["a", "b", "r"]);
  });
});
