import { describe, expect, it } from "vitest";
import { ARCHIVED_SHARED_STEP, buildSharedStep } from "../test/utils/shared-step.fixture";
import {
  buildSharedStepFormValues,
  buildUpdateSharedStepRequest,
  checkHasSharedStepChanges,
  checkHasSharedStepFormErrors,
  createEmptySharedStepFormValues,
  listInsertableSharedSteps,
  normalizeSharedStepKey,
  validateSharedStepForm,
} from "./shared-step-form.util";

const SHARED_STEP = buildSharedStep();

describe("validateSharedStepForm", () => {
  it("requires a title, a valid key and an action on every step", () => {
    const values = { ...createEmptySharedStepFormValues(), key: "9lives" };
    const errors = validateSharedStepForm(values);

    expect(errors.title).toBe("required");
    expect(errors.key).toBe("invalidKey");
    expect(Object.values(errors.stepActions)).toEqual(["required"]);
    expect(checkHasSharedStepFormErrors(errors)).toBe(true);
  });

  it("accepts a key in any case and a filled step", () => {
    const values = buildSharedStepFormValues(SHARED_STEP);

    expect(checkHasSharedStepFormErrors(validateSharedStepForm({ ...values, key: "Log_In" }))).toBe(
      false,
    );
    expect(normalizeSharedStepKey("  Log_In ")).toBe("log_in");
  });

  it("refuses a shared step without steps", () => {
    const values = { ...buildSharedStepFormValues(SHARED_STEP), steps: [] };

    expect(validateSharedStepForm(values).steps).toBe("required");
  });
});

describe("buildUpdateSharedStepRequest", () => {
  it("sends only the base version when nothing changed", () => {
    const request = buildUpdateSharedStepRequest(
      buildSharedStepFormValues(SHARED_STEP),
      SHARED_STEP,
    );

    expect(request).toEqual({ baseVersionNumber: 2 });
    expect(checkHasSharedStepChanges(request)).toBe(false);
  });

  it("sends a new title alone, so no version is added", () => {
    const values = { ...buildSharedStepFormValues(SHARED_STEP), title: " Sign in as admin " };

    expect(buildUpdateSharedStepRequest(values, SHARED_STEP)).toEqual({
      baseVersionNumber: 2,
      title: "Sign in as admin",
    });
  });
});

describe("listInsertableSharedSteps", () => {
  it("leaves out archived shared steps", () => {
    expect(listInsertableSharedSteps([SHARED_STEP, ARCHIVED_SHARED_STEP])).toEqual([SHARED_STEP]);
  });
});
