import { describe, expect, it } from "vitest";
import { buildLabel, CHECKOUT_LABEL_ID, toCaseLabel } from "../test/utils/label-fixture.util";
import { buildLabelOptions, checkHasSameLabelIds } from "./label-options.util";

const smoke = buildLabel();
const checkout = buildLabel({ id: CHECKOUT_LABEL_ID, name: "checkout", color: "blue" });

describe("label options", () => {
  it("offers the project's labels and keeps a selected label the list no longer has", () => {
    expect(buildLabelOptions([smoke], [toCaseLabel(checkout)])).toEqual([
      { value: smoke.id, label: "smoke" },
      { value: checkout.id, label: "checkout" },
    ]);
  });

  it("compares the chosen ids with the case's labels in any order", () => {
    const caseLabels = [toCaseLabel(smoke), toCaseLabel(checkout)];

    expect(checkHasSameLabelIds([checkout.id, smoke.id], caseLabels)).toBe(true);
    expect(checkHasSameLabelIds([smoke.id], caseLabels)).toBe(false);
    expect(checkHasSameLabelIds([], [])).toBe(true);
  });
});
