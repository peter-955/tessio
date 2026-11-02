import { describe, expect, it } from "vitest";
import { buildSuiteOptions, type SuiteOptionSource } from "./suite-options.util";

const SUITE_ID = "c1000000-0000-4000-8000-000000000001";

const OTHER_SUITE_ID = "c1000000-0000-4000-8000-000000000002";

const CHECKOUT: SuiteOptionSource = { id: SUITE_ID, name: "Checkout regression", archivedAt: null };

const toArchivedLabel = (name: string): string => `${name} (archived)`;

describe("buildSuiteOptions", () => {
  it("lists the suites and labels the archived ones", () => {
    const archived = { id: OTHER_SUITE_ID, name: "Old", archivedAt: "2026-10-25T10:00:00Z" };

    expect(buildSuiteOptions([CHECKOUT, archived], SUITE_ID, toArchivedLabel)).toEqual([
      { value: SUITE_ID, label: "Checkout regression" },
      { value: OTHER_SUITE_ID, label: "Old (archived)" },
    ]);
  });

  it("names a chosen suite that is not in the list with the loaded suite, never its id", () => {
    expect(buildSuiteOptions([], SUITE_ID, toArchivedLabel, CHECKOUT)).toEqual([
      { value: SUITE_ID, label: "Checkout regression" },
    ]);
    expect(
      buildSuiteOptions([], SUITE_ID, toArchivedLabel, {
        ...CHECKOUT,
        archivedAt: "2026-10-25T10:00:00Z",
      }),
    ).toEqual([{ value: SUITE_ID, label: "Checkout regression (archived)" }]);
  });

  it("adds no option with the raw id while the chosen suite is still loading", () => {
    expect(buildSuiteOptions([], SUITE_ID, toArchivedLabel)).toEqual([]);
    expect(
      buildSuiteOptions([], SUITE_ID, toArchivedLabel, { ...CHECKOUT, id: OTHER_SUITE_ID }),
    ).toEqual([]);
  });
});
