import { describe, expect, it } from "vitest";
import { buildLabel } from "../test/utils/label-fixture.util";
import {
  buildCreateLabelRequest,
  buildLabelFormValues,
  buildUpdateLabelRequest,
} from "./label-request.util";

describe("label request", () => {
  it("starts a new label as gray and trims the name", () => {
    expect(buildLabelFormValues(null)).toEqual({ name: "", color: "gray" });
    expect(buildCreateLabelRequest({ name: "  smoke ", color: "red" })).toEqual({
      name: "smoke",
      color: "red",
    });
  });

  it("sends only the fields that changed", () => {
    const label = buildLabel();

    expect(buildUpdateLabelRequest({ name: " smoke ", color: "green" }, label)).toEqual({});
    expect(buildUpdateLabelRequest({ name: "Smoke", color: "green" }, label)).toEqual({
      name: "Smoke",
    });
    expect(buildUpdateLabelRequest({ name: "smoke", color: "teal" }, label)).toEqual({
      color: "teal",
    });
  });
});
