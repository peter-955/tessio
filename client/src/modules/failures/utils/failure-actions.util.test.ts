import { describe, expect, it } from "vitest";
import {
  DEV_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "../test/utils/project-fixture.util";
import { buildFailureStatusActions } from "./failure-actions.util";

const DEV_PROJECT = { capabilities: DEV_CAPABILITIES, isArchived: false };
const QC_PROJECT = { capabilities: QC_CAPABILITIES, isArchived: false };
const VIEWER_PROJECT = { capabilities: VIEWER_CAPABILITIES, isArchived: false };

describe("buildFailureStatusActions", () => {
  it("lets a developer mark an open or reopened failure fixed", () => {
    const markFixed = [{ status: "fixed", labelKey: "markFixed", type: "primary" }];

    expect(buildFailureStatusActions("open", DEV_PROJECT)).toEqual(markFixed);
    expect(buildFailureStatusActions("reopened", DEV_PROJECT)).toEqual(markFixed);
    expect(buildFailureStatusActions("fixed", DEV_PROJECT)).toEqual([]);
  });

  it("lets a tester verify or reopen a fixed failure", () => {
    expect(buildFailureStatusActions("fixed", QC_PROJECT)).toEqual([
      { status: "verified", labelKey: "verify", type: "primary" },
      { status: "reopened", labelKey: "reopen", type: "default" },
    ]);
    expect(buildFailureStatusActions("open", QC_PROJECT)).toEqual([]);
  });

  it("offers nothing on verified failures, to viewers or on archived projects", () => {
    expect(buildFailureStatusActions("verified", QC_PROJECT)).toEqual([]);
    expect(buildFailureStatusActions("verified", DEV_PROJECT)).toEqual([]);
    expect(buildFailureStatusActions("open", VIEWER_PROJECT)).toEqual([]);
    expect(buildFailureStatusActions("fixed", VIEWER_PROJECT)).toEqual([]);
    expect(buildFailureStatusActions("open", { ...DEV_PROJECT, isArchived: true })).toEqual([]);
    expect(buildFailureStatusActions("fixed", { ...QC_PROJECT, isArchived: true })).toEqual([]);
  });
});
