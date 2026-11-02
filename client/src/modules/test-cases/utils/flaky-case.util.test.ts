import { describe, expect, it } from "vitest";
import { buildProject } from "../test/utils/project-fixture.util";
import {
  buildQuarantineRequest,
  checkCanQuarantineTestCases,
  listFlakyCaseBadges,
} from "./flaky-case.util";

const NO_FLAGS = { isFlaky: false, isDisagreeing: false, isQuarantined: false };

describe("checkCanQuarantineTestCases", () => {
  it("needs test_case.quarantine on a project that is not archived", () => {
    expect(
      checkCanQuarantineTestCases(buildProject({ capabilities: ["test_case.quarantine"] })),
    ).toBe(true);
    expect(checkCanQuarantineTestCases(buildProject({ capabilities: ["test_case.edit"] }))).toBe(
      false,
    );
    expect(
      checkCanQuarantineTestCases(
        buildProject({ capabilities: ["test_case.quarantine"], isArchived: true }),
      ),
    ).toBe(false);
  });
});

describe("listFlakyCaseBadges", () => {
  it("lists no badge for a healthy case", () => {
    expect(listFlakyCaseBadges(NO_FLAGS)).toEqual([]);
  });

  it("lists flaky, disagreeing and quarantined in that order", () => {
    const kinds = listFlakyCaseBadges({
      isFlaky: true,
      isDisagreeing: true,
      isQuarantined: true,
    }).map((badge) => badge.kind);

    expect(kinds).toEqual(["flaky", "disagreeing", "quarantined"]);
  });

  it("lists only the flags that are set", () => {
    expect(
      listFlakyCaseBadges({ ...NO_FLAGS, isQuarantined: true }).map((badge) => badge.kind),
    ).toEqual(["quarantined"]);
    expect(
      listFlakyCaseBadges({ ...NO_FLAGS, isDisagreeing: true }).map((badge) => badge.icon),
    ).toEqual(["alert"]);
  });
});

describe("buildQuarantineRequest", () => {
  it("sends the trimmed reason", () => {
    expect(buildQuarantineRequest("  Fails at random  ")).toEqual({ reason: "Fails at random" });
  });

  it("sends no reason when it is blank", () => {
    expect(buildQuarantineRequest("")).toEqual({});
    expect(buildQuarantineRequest("   ")).toEqual({});
  });
});
