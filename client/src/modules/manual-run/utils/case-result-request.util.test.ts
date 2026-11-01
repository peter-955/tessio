import { describe, expect, it } from "vitest";
import { buildStep } from "../test/utils/run.fixture";
import type { CaseDraft } from "../typing/types/case-draft.type";
import {
  buildCaseResultRequest,
  checkIsCaseDraftUploading,
  createEmptyCaseDraft,
} from "./case-result-request.util";
import { createEmptyStepDraft } from "./step-draft.util";

const STEPS = [buildStep({ order: 1 }), buildStep({ order: 2 }), buildStep({ order: 3 })];

const EVIDENCE_FILE = {
  id: "f1000000-0000-4000-8000-000000000001",
  kind: "evidence" as const,
  fileName: "cart.png",
  contentType: "image/png",
  size: 10,
  status: "uploaded" as const,
  createdAt: "2026-10-01T09:00:00Z",
};

describe("buildCaseResultRequest", () => {
  it("omits steps without a status and keeps the suggestion by default", () => {
    const draft: CaseDraft = {
      statusOverride: null,
      steps: {
        1: { ...createEmptyStepDraft(), status: "passed", actualResult: "  Opened  " },
        2: { ...createEmptyStepDraft(), actualResult: "Typed but not marked" },
      },
    };

    expect(buildCaseResultRequest(draft, STEPS)).toEqual({
      status: null,
      durationMs: null,
      steps: [
        { order: 1, status: "passed", actualResult: "Opened", error: null, evidenceFileId: null },
      ],
    });
  });

  it("trims the error, turns an empty error into null and sends the evidence id", () => {
    const draft: CaseDraft = {
      statusOverride: null,
      steps: {
        1: { ...createEmptyStepDraft(), status: "failed", error: "  Declined  " },
        2: { ...createEmptyStepDraft(), status: "blocked", error: "   " },
        3: { ...createEmptyStepDraft(), status: "passed", evidenceFile: EVIDENCE_FILE },
      },
    };

    expect(buildCaseResultRequest(draft, STEPS).steps).toEqual([
      { order: 1, status: "failed", actualResult: "", error: "Declined", evidenceFileId: null },
      { order: 2, status: "blocked", actualResult: "", error: null, evidenceFileId: null },
      {
        order: 3,
        status: "passed",
        actualResult: "",
        error: null,
        evidenceFileId: EVIDENCE_FILE.id,
      },
    ]);
  });

  it("drops an error typed before the step was marked passed", () => {
    const draft: CaseDraft = {
      statusOverride: null,
      steps: { 1: { ...createEmptyStepDraft(), status: "passed", error: "Old error" } },
    };

    expect(buildCaseResultRequest(draft, STEPS).steps?.[0]?.error).toBeNull();
  });

  it("sends the override status", () => {
    const draft: CaseDraft = { ...createEmptyCaseDraft(), statusOverride: "blocked" };

    expect(buildCaseResultRequest(draft, STEPS)).toEqual({
      status: "blocked",
      durationMs: null,
      steps: [],
    });
  });
});

describe("checkIsCaseDraftUploading", () => {
  it("is true only while a step upload runs", () => {
    expect(checkIsCaseDraftUploading(createEmptyCaseDraft())).toBe(false);
    expect(
      checkIsCaseDraftUploading({
        statusOverride: null,
        steps: { 2: { ...createEmptyStepDraft(), isUploading: true } },
      }),
    ).toBe(true);
  });
});
