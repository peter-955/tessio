import { describe, expect, it } from "vitest";
import { normalizeProjectKeyInput, suggestProjectKey } from "./project-key.util";

describe("suggestProjectKey", () => {
  it("keeps a Jira key that is already a valid project key", () => {
    expect(suggestProjectKey("SHOP", "Online shop")).toBe("SHOP");
  });

  it("builds the key from the name when the Jira key is not valid", () => {
    expect(suggestProjectKey("SH_OP", "Online shop")).toBe("ONLINESHOP");
  });

  it("drops leading digits and keeps at most 10 characters", () => {
    expect(suggestProjectKey("1A", "2024 customer portal")).toBe("CUSTOMERPO");
  });

  it("returns an empty key when fewer than 2 characters are left", () => {
    expect(suggestProjectKey("x", "9 é")).toBe("");
  });
});

describe("normalizeProjectKeyInput", () => {
  it("uppercases and strips characters outside A-Z and 0-9", () => {
    expect(normalizeProjectKeyInput("sh-op 2!")).toBe("SHOP2");
  });
});
