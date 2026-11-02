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
        { order: 1, action: "Open the cart", expected: null, sharedStepKey: null },
        {
          order: 2,
          action: "Pay as {{data.admin}}",
          expected: "The order is paid",
          sharedStepKey: null,
        },
        { order: 3, action: "Open the receipt", expected: null, sharedStepKey: null },
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

  it("reports a version that changes only the parameters and data rows", () => {
    const withRows = buildTestCaseVersion({
      ...OLDER,
      id: "newer",
      number: 2,
      parameters: ["email"],
      dataRows: [{ email: "ann@shop.test" }],
    });
    const withMoreRows = buildTestCaseVersion({
      ...withRows,
      id: "newest",
      number: 3,
      dataRows: [{ email: "ann@shop.test" }, { email: "bob@shop.test" }],
    });

    expect(buildVersionDiff(OLDER, withRows, STORY_CRITERIA)).toEqual([
      {
        field: "dataTable",
        kind: "dataTable",
        tokens: [{ value: "email\n1. ann@shop.test", kind: "added" }],
      },
    ]);
    const entries = buildVersionDiff(withRows, withMoreRows, STORY_CRITERIA);
    const [entry] = entries;

    expect(entries.map((item) => item.field)).toEqual(["dataTable"]);
    expect(entry?.kind === "dataTable" ? entry.tokens : []).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ kind: "added", value: expect.stringContaining("bob@shop.test") }),
      ]),
    );
    expect(
      entry?.kind === "dataTable" && entry.tokens.every((token) => token.kind !== "removed"),
    ).toBe(true);
  });

  it("reports removed steps and cleared text", () => {
    const newer = buildTestCaseVersion({
      id: "newer",
      number: 2,
      businessValue: null,
      steps: [{ order: 1, action: "Open the cart", expected: null, sharedStepKey: null }],
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
