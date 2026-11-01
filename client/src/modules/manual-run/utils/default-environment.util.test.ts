import { describe, expect, it } from "vitest";
import { PRODUCTION_ID, STAGING_ID } from "../test/utils/run.fixture";
import { pickDefaultEnvironmentId } from "./default-environment.util";

describe("pickDefaultEnvironmentId", () => {
  it("returns the project default when it is listed", () => {
    expect(
      pickDefaultEnvironmentId([{ id: STAGING_ID }, { id: PRODUCTION_ID }], PRODUCTION_ID),
    ).toBe(PRODUCTION_ID);
  });

  it("returns the only environment when the default is missing", () => {
    expect(pickDefaultEnvironmentId([{ id: STAGING_ID }], PRODUCTION_ID)).toBe(STAGING_ID);
    expect(pickDefaultEnvironmentId([{ id: STAGING_ID }], null)).toBe(STAGING_ID);
  });

  it("returns null when several environments have no listed default", () => {
    expect(pickDefaultEnvironmentId([{ id: STAGING_ID }, { id: PRODUCTION_ID }], null)).toBeNull();
    expect(pickDefaultEnvironmentId([], STAGING_ID)).toBeNull();
  });
});
