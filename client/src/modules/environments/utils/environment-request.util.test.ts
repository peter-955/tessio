import { describe, expect, it } from "vitest";
import { buildEnvironment } from "../test/utils/environment-fixture.util";
import { buildEnvironmentFormValues, buildEnvironmentRequest } from "./environment-request.util";

describe("buildEnvironmentRequest", () => {
  it("trims the values and sends an empty health-check URL as null", () => {
    expect(
      buildEnvironmentRequest({
        name: "  Staging ",
        baseUrl: " https://staging.example.test ",
        healthCheckUrl: "   ",
      }),
    ).toEqual({ name: "Staging", baseUrl: "https://staging.example.test", healthCheckUrl: null });
  });

  it("keeps a filled health-check URL", () => {
    expect(
      buildEnvironmentRequest({
        name: "Staging",
        baseUrl: "https://staging.example.test",
        healthCheckUrl: "https://staging.example.test/health",
      }).healthCheckUrl,
    ).toBe("https://staging.example.test/health");
  });
});

describe("buildEnvironmentFormValues", () => {
  it("starts empty for a new environment", () => {
    expect(buildEnvironmentFormValues(null)).toEqual({ name: "", baseUrl: "", healthCheckUrl: "" });
  });

  it("copies an existing environment", () => {
    expect(buildEnvironmentFormValues(buildEnvironment({ healthCheckUrl: null }))).toEqual({
      name: "Staging",
      baseUrl: "https://staging.example.test",
      healthCheckUrl: "",
    });
  });
});
