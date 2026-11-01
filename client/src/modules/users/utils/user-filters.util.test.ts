import { describe, expect, it } from "vitest";
import { buildUserListQuery } from "./user-filters.util";

describe("buildUserListQuery", () => {
  it("drops null filters and a blank query", () => {
    expect(buildUserListQuery({ status: null, workspaceRole: null, query: "   " })).toEqual({});
  });

  it("keeps set filters and trims the query", () => {
    expect(
      buildUserListQuery({ status: "deactivated", workspaceRole: "admin", query: "  ada " }),
    ).toEqual({ status: "deactivated", workspaceRole: "admin", query: "ada" });
  });
});
