import { describe, expect, it } from "vitest";
import { buildStoryRequest, moveCriterion } from "./story-editor.util";

describe("buildStoryRequest", () => {
  it("trims the fields and leaves out empty criteria", () => {
    expect(
      buildStoryRequest({
        title: "  Pay by card ",
        description: "   ",
        criteria: [
          { id: "1", text: " Card accepted " },
          { id: "2", text: "  " },
        ],
      }),
    ).toEqual({ title: "Pay by card", description: null, criteria: ["Card accepted"] });
  });
});

describe("moveCriterion", () => {
  const criteria = [
    { id: "1", text: "A" },
    { id: "2", text: "B" },
    { id: "3", text: "C" },
  ];

  it("moves a criterion up or down", () => {
    expect(moveCriterion(criteria, 2, -1).map((criterion) => criterion.text)).toEqual([
      "A",
      "C",
      "B",
    ]);
    expect(moveCriterion(criteria, 0, 1).map((criterion) => criterion.text)).toEqual([
      "B",
      "A",
      "C",
    ]);
  });

  it("keeps the order at the edges", () => {
    expect(moveCriterion(criteria, 0, -1).map((criterion) => criterion.text)).toEqual([
      "A",
      "B",
      "C",
    ]);
  });
});
