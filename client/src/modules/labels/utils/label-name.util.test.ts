import { describe, expect, it } from "vitest";
import { buildLabel, CHECKOUT_LABEL_ID, SMOKE_LABEL_ID } from "../test/utils/label-fixture.util";
import { findLabelByName, findLabelNameError } from "./label-name.util";

const labels = [buildLabel(), buildLabel({ id: CHECKOUT_LABEL_ID, name: "Checkout" })];

describe("label name", () => {
  it("finds a label by name without regard to case or surrounding spaces", () => {
    expect(findLabelByName(labels, "  CHECKOUT ")?.id).toBe(CHECKOUT_LABEL_ID);
    expect(findLabelByName(labels, "regression")).toBeUndefined();
  });

  it("needs 1 to 40 characters after trimming", () => {
    expect(findLabelNameError("   ", labels)).toBe("required");
    expect(findLabelNameError("a".repeat(41), labels)).toBe("tooLong");
    expect(findLabelNameError(` ${"a".repeat(40)} `, labels)).toBeNull();
  });

  it("refuses another label's name but lets a label change the case of its own", () => {
    expect(findLabelNameError("SMOKE", labels)).toBe("alreadyUsed");
    expect(findLabelNameError("SMOKE", labels, SMOKE_LABEL_ID)).toBeNull();
    expect(findLabelNameError("checkout", labels, SMOKE_LABEL_ID)).toBe("alreadyUsed");
  });
});
