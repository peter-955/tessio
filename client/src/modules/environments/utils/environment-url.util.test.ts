import { describe, expect, it } from "vitest";
import { MAX_ENVIRONMENT_URL_LENGTH } from "../typing/constants/environment.constant";
import { findEnvironmentUrlError } from "./environment-url.util";

describe("findEnvironmentUrlError", () => {
  it.each(["https://staging.example.test", "http://localhost:3000/app", " https://a.test "])(
    "accepts %s",
    (url) => {
      expect(findEnvironmentUrlError(url)).toBeNull();
    },
  );

  it.each(["", "staging.example.test", "ftp://example.test", "https://a b.test"])(
    "rejects %s",
    (url) => {
      expect(findEnvironmentUrlError(url)).toBe("invalid");
    },
  );

  it("rejects a URL longer than the limit", () => {
    const url = `https://${"a".repeat(MAX_ENVIRONMENT_URL_LENGTH)}`;

    expect(findEnvironmentUrlError(url)).toBe("tooLong");
  });
});
