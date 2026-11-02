import { describe, expect, it } from "vitest";
import {
  fillOptionalParameters,
  fillParameters,
  formatIterationNumber,
} from "./parameter-text.util";

describe("fillParameters", () => {
  it("puts the row values in place of the parameter references", () => {
    expect(
      fillParameters("Sign in as {{param.email}} with role {{param.role}}", {
        email: "{{data.qc_email}}",
        role: "qc",
      }),
    ).toBe("Sign in as {{data.qc_email}} with role qc");
  });

  it("leaves unknown parameters and other references as they are", () => {
    expect(fillParameters("Use {{param.missing}} and {{data.key}}", { email: "a" })).toBe(
      "Use {{param.missing}} and {{data.key}}",
    );
    expect(fillParameters("{{param.constructor}}", {})).toBe("{{param.constructor}}");
    expect(fillOptionalParameters(null, { email: "a" })).toBeNull();
  });

  it("numbers iterations from 1 for people", () => {
    expect(formatIterationNumber(0)).toBe(1);
  });
});
