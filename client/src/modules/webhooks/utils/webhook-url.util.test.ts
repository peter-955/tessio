import { describe, expect, it } from "vitest";
import { findWebhookUrlError } from "./webhook-url.util";

describe("findWebhookUrlError", () => {
  it("accepts a public https URL", () => {
    expect(findWebhookUrlError(" https://ci.example.com/hooks/tessio?x=1 ")).toBeNull();
  });

  it("asks for a URL when it is empty", () => {
    expect(findWebhookUrlError("   ")).toBe("required");
  });

  it("refuses a URL over 2048 characters", () => {
    expect(findWebhookUrlError(`https://ci.example.com/${"a".repeat(2048)}`)).toBe("tooLong");
  });

  it("refuses http and other schemes", () => {
    expect(findWebhookUrlError("http://ci.example.com/hook")).toBe("notHttps");
    expect(findWebhookUrlError("ftp://ci.example.com/hook")).toBe("notHttps");
  });

  it("refuses text that is not a URL, a host without a dot and user info", () => {
    expect(findWebhookUrlError("ci.example.com")).toBe("invalid");
    expect(findWebhookUrlError("https://localhost/hook")).toBe("invalid");
    expect(findWebhookUrlError("https://user:pass@ci.example.com/hook")).toBe("invalid");
    expect(findWebhookUrlError("https://ci.example.com/a b")).toBe("invalid");
  });
});
