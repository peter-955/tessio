import { describe, expect, it } from "vitest";
import { buildLabel, CHECKOUT_LABEL_ID } from "../test/utils/label-fixture.util";
import { buildLabelFilterChoices, normalizeLabelNames, parseLabelNames } from "./label-filter.util";

describe("label filter", () => {
  it("reads one or many label names from the URL", () => {
    expect(parseLabelNames(undefined)).toEqual([]);
    expect(parseLabelNames("smoke")).toEqual(["smoke"]);
    expect(parseLabelNames(["smoke", "checkout"])).toEqual(["smoke", "checkout"]);
  });

  it("trims names, drops blank and too long ones and repeats without regard to case", () => {
    expect(parseLabelNames([" smoke ", "", "  ", "SMOKE", "a".repeat(41), "checkout"])).toEqual([
      "smoke",
      "checkout",
    ]);
  });

  it("keeps at most 20 names", () => {
    const names = Array.from({ length: 25 }, (_, index) => `label-${index}`);

    expect(normalizeLabelNames(names)).toEqual(names.slice(0, 20));
  });

  it("shows a chosen name as the label's own name and keeps unknown names", () => {
    const labels = [
      buildLabel(),
      buildLabel({ id: CHECKOUT_LABEL_ID, name: "Checkout", color: "blue" }),
    ];

    expect(buildLabelFilterChoices(labels, ["CHECKOUT", "legacy"])).toEqual({
      options: [
        { value: "smoke", label: "smoke" },
        { value: "Checkout", label: "Checkout" },
        { value: "legacy", label: "legacy" },
      ],
      value: ["Checkout", "legacy"],
    });
  });
});
