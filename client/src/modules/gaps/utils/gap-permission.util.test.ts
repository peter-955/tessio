import { describe, expect, it } from "vitest";
import { CURRENT_USER_ID, createGap, createResolvedGap } from "../test/utils/gap.fixture";
import { canReopenGap } from "./gap-permission.util";

const RESOLVED_GAP = createResolvedGap();
const OWN_RESOLVED_GAP = createResolvedGap({ raisedBy: CURRENT_USER_ID });

describe("canReopenGap", () => {
  it("lets the raiser reopen whatever their role", () => {
    expect(canReopenGap(OWN_RESOLVED_GAP, CURRENT_USER_ID, "dev", true)).toBe(true);
    expect(canReopenGap(OWN_RESOLVED_GAP, CURRENT_USER_ID, null, true)).toBe(true);
  });

  it("lets qc and admin reopen gaps raised by someone else", () => {
    expect(canReopenGap(RESOLVED_GAP, CURRENT_USER_ID, "qc", true)).toBe(true);
    expect(canReopenGap(RESOLVED_GAP, CURRENT_USER_ID, "admin", true)).toBe(true);
    expect(canReopenGap(RESOLVED_GAP, CURRENT_USER_ID, "dev", true)).toBe(false);
    expect(canReopenGap(RESOLVED_GAP, CURRENT_USER_ID, null, true)).toBe(false);
  });

  it("needs gap.raise and a resolved gap", () => {
    expect(canReopenGap(OWN_RESOLVED_GAP, CURRENT_USER_ID, "qc", false)).toBe(false);
    expect(
      canReopenGap(createGap({ raisedBy: CURRENT_USER_ID }), CURRENT_USER_ID, "qc", true),
    ).toBe(false);
  });
});
