import { describe, expect, it } from "vitest";
import { buildRunSuiteCommand } from "./suite-command.util";

const SUITE_ID = "5a000000-0000-4000-8000-000000000001";

describe("buildRunSuiteCommand", () => {
  it("names a one-word suite as it is", () => {
    expect(buildRunSuiteCommand({ id: SUITE_ID, name: "smoke" })).toBe("/tessio:run-suite smoke");
  });

  it("quotes a name with spaces", () => {
    expect(buildRunSuiteCommand({ id: SUITE_ID, name: "Checkout regression" })).toBe(
      '/tessio:run-suite "Checkout regression"',
    );
  });

  it("uses the suite id when the name holds a quote", () => {
    expect(buildRunSuiteCommand({ id: SUITE_ID, name: 'The "big" one' })).toBe(
      `/tessio:run-suite ${SUITE_ID}`,
    );
  });
});
