import { describe, expect, it } from "vitest";
import { buildJunitImportFormData } from "./junit-import-form-data.util";

describe("buildJunitImportFormData", () => {
  it("sends the file, the environment and the suite as multipart fields", () => {
    const file = new File(["<testsuites/>"], "results.xml", { type: "text/xml" });

    const formData = buildJunitImportFormData({ file, environment: "env-1", suite: "suite-1" });

    expect((formData.get("file") as File).name).toBe("results.xml");
    expect(formData.get("environment")).toBe("env-1");
    expect(formData.get("suite")).toBe("suite-1");
  });

  it("leaves out the suite when none is chosen", () => {
    const file = new File(["<testsuites/>"], "results.xml", { type: "text/xml" });

    expect(buildJunitImportFormData({ file, environment: "env-1", suite: null }).has("suite")).toBe(
      false,
    );
  });
});
