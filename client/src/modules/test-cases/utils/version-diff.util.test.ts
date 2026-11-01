import { describe, expect, it } from "vitest";
import {
  FIRST_CRITERION_ID,
  SECOND_CRITERION_ID,
  STORY_CRITERIA,
  buildTestCaseVersion,
} from "../test/utils/test-case-fixture.util";
import { buildVersionDiff, buildWordDiff } from "./version-diff.util";

const OLDER = buildTestCaseVersion({ id: "older", number: 1, fileVersionIds: ["file-1"] });

describe("buildWordDiff", () => {
  it("marks added and removed words", () => {
    expect(buildWordDiff("Pay with a card", "Pay with a saved card")).toEqual([
      { value: "Pay with a ", kind: "unchanged" },
      { value: "saved ", kind: "added" },
      { value: "card", kind: "unchanged" },
    ]);
  });
});

describe("buildVersionDiff", () => {
  it("returns no entries for identical versions", () => {
    expect(buildVersionDiff(OLDER, { ...OLDER, id: "newer", number: 2 }, STORY_CRITERIA)).toEqual(
      [],
    );
  });

  it("lists only the changed fields", () => {
    const newer = buildTestCaseVersion({
      id: "newer",
      number: 2,
      title: "Pay with a saved card",
      priority: "critical",
      steps: [
        { order: 1, action: "Open the cart", expected: null },
        { order: 2, action: "Pay as {{data.admin}}", expected: "The order is paid" },
        { order: 3, action: "Open the receipt", expected: null },
      ],
      criterionIds: [SECOND_CRITERION_ID],
      fileVersionIds: ["file-2", "file-3"],
    });

    const entries = buildVersionDiff(OLDER, newer, STORY_CRITERIA);

    expect(entries.map((entry) => entry.field)).toEqual([
      "title",
      "priority",
      "steps",
      "criteria",
      "files",
    ]);
    expect(entries[1]).toEqual({
      field: "priority",
      kind: "priority",
      from: "high",
      to: "critical",
    });
    expect(entries[2]).toMatchObject({
      kind: "steps",
      steps: [
        { position: 2, change: "changed" },
        { position: 3, change: "added", action: [{ value: "Open the receipt", kind: "added" }] },
      ],
    });
    expect(entries[3]).toEqual({
      field: "criteria",
      kind: "criteria",
      tokens: [
        { value: "AC1", kind: "removed" },
        { value: "AC2", kind: "added" },
      ],
    });
    expect(entries[4]).toEqual({ field: "files", kind: "files", added: 2, removed: 1 });
  });

  it("reports removed steps and cleared text", () => {
    const newer = buildTestCaseVersion({
      id: "newer",
      number: 2,
      businessValue: null,
      steps: [{ order: 1, action: "Open the cart", expected: null }],
      criterionIds: [FIRST_CRITERION_ID],
      fileVersionIds: ["file-1"],
    });

    const entries = buildVersionDiff(OLDER, newer, STORY_CRITERIA);

    expect(entries.map((entry) => entry.field)).toEqual(["businessValue", "steps"]);
    expect(entries[0]).toEqual({
      field: "businessValue",
      kind: "text",
      tokens: [{ value: "Customers can pay", kind: "removed" }],
    });
    expect(entries[1]).toMatchObject({ steps: [{ position: 2, change: "removed" }] });
  });
});
